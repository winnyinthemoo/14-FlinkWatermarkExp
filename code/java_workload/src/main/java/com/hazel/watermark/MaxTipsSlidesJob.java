package com.hazel.watermark;

import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple4;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.timestamps.BoundedOutOfOrdernessTimestampExtractor;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;
import org.apache.flink.util.OutputTag;

public class MaxTipsSlidesJob {

    public static void main(String[] args) throws Exception {

        // ========== ① 读取外部参数 (watermark 延迟分钟) ==========
        int watermarkMinutes = 30; // default
        if (args.length > 0) {
            try {
                watermarkMinutes = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                System.out.println("参数无效，使用默认 Watermark 延迟: 30 分钟");
            }
        }
        System.out.println("使用 Watermark 延迟 = " + watermarkMinutes + " 分钟");

        // ============================================================
        // 1. 创建执行环境
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // 2. 设置时间语义为 EventTime
        env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
        env.getConfig().setAutoWatermarkInterval(5);
        // 3. 数据源
        DataStream<TaxiFare> stream = env.addSource(
                new TaxiFareParquetSource("C:\\Users\\alex\\Downloads\\yellow_tripdata_2024-02_first300k.parquet",watermarkMinutes*60*1000)
                // new TaxiFareSource("C:\\Users\\alex\\Downloads\\Taxi_Trips_(2024-)_20251206_shuffled.csv")
        ).setParallelism(1);

        // ========== ② 使用动态 Watermark 参数 ==========
        SingleOutputStreamOperator<TaxiFare> dataStream = stream.assignTimestampsAndWatermarks(
                new BoundedOutOfOrdernessTimestampExtractor<TaxiFare>(Time.minutes(watermarkMinutes)) {
                    @Override
                    public long extractTimestamp(TaxiFare element) {
                        return element.startTime.toEpochMilli();
                    }
                }
        );

        // 5. Map 转换
        SingleOutputStreamOperator<Tuple2<String, Float>> mapStream = dataStream
                .map((MapFunction<TaxiFare, Tuple2<String, Float>>) value ->
                        new Tuple2<>(value.taxiId, value.tip)
                )
                .returns(Types.TUPLE(Types.STRING, Types.FLOAT))
                .setParallelism(4);

        // 6. 侧输出流 (迟到数据)
        OutputTag<Tuple2<String, Float>> lateTag = new OutputTag<Tuple2<String, Float>>("late"){};

        // 7. 窗口聚合
        int finalWatermarkMinutes = watermarkMinutes;
        SingleOutputStreamOperator<Tuple4<Long, String, Float, Long>> sumById = mapStream
                .keyBy(t -> t.f0)
                .timeWindow(Time.hours(1), Time.minutes(30))
                .allowedLateness(Time.seconds(0))
                .sideOutputLateData(lateTag)
                .process(new ProcessWindowFunction<Tuple2<String, Float>, Tuple4<Long, String, Float,Long>, String, TimeWindow>() {
                    @Override
                    public void process(String key,
                                        Context context,
                                        Iterable<Tuple2<String, Float>> elements,
                                        Collector<Tuple4<Long, String, Float,Long>> out) {
                        float sum = 0f;
                        for (Tuple2<String, Float> e : elements) {
                            sum += e.f1;
                        }
                        long windowStart = context.window().getStart();
                        long watermark=context.currentWatermark();
                        long delay= watermark+ (long) finalWatermarkMinutes *60*1000 -context.window().getEnd();
                        if(watermark == Long.MAX_VALUE) {
                            delay = -1; //special
                        }
                        out.collect(new Tuple4<>(windowStart, key, sum, delay));
                    }
                })
                .setParallelism(4);

        // 迟到数据统计
        DataStream<Tuple2<String, Float>> lateStream = sumById.getSideOutput(lateTag);
        SingleOutputStreamOperator<Integer> lateCount = lateStream
                .map(f -> 1)
                .returns(Integer.class)
                .keyBy(f -> 0)
                .sum(0)
                .setParallelism(1);

        lateCount.print("Total Late Data");
        sumById.addSink(new SingleFileSink("C:\\Users\\Public\\slide_window_result_"+Integer.toString(watermarkMinutes)+".txt")).setParallelism(4);

        // 10. 执行任务
        env.execute("Flink Watermark Experiment");
    }
}
