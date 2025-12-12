package com.hazel.watermark;

import org.apache.flink.api.common.functions.ReduceFunction;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.KeyedStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.sink.DiscardingSink;
import org.apache.flink.streaming.api.windowing.assigners.SlidingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.Window;
import org.apache.flink.streaming.api.functions.windowing.WindowFunction;
import org.apache.flink.util.Collector;

import java.io.Serializable;
import java.util.Random;

/**
 * 完整可运行的老版本 ProcessingTime Window 示例。
 * Flink 1.9 - 1.13 兼容。
 */
public class GroupedProcessingTimeWindowExample {

    public static void main(String[] args) throws Exception {
        final ParameterTool params = ParameterTool.fromArgs(args);
        final boolean asyncState = params.has("async-state");

        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        final long numElementsPerParallel = 2000000; // 为演示缩小数量
        final long numKeys = 10000;

        // 显式可序列化 DataGeneratorSource
        DataStream<Tuple2<Long, Long>> stream = env.addSource(
                new DataGeneratorSource(numElementsPerParallel, numKeys)
        ).returns(Types.TUPLE(Types.LONG, Types.LONG));

        KeyedStream<Tuple2<Long, Long>, Long> keyedStream = stream.keyBy(value -> value.f0);

        // asyncState 可选处理
//        if (asyncState) {
//            keyedStream = keyedStream.enableAsyncState();
//        }

        keyedStream
                .window(SlidingProcessingTimeWindows.of(Time.milliseconds(2500), Time.milliseconds(500)))
                .reduce(new SummingReducer())
                .addSink(new DiscardingSink<>());

        env.execute("Grouped Processing Time Window Example");
    }

    // ------------------------------------------------------------------------------------------
    // Reducer
    private static class SummingReducer implements ReduceFunction<Tuple2<Long, Long>> {
        @Override
        public Tuple2<Long, Long> reduce(Tuple2<Long, Long> value1, Tuple2<Long, Long> value2) {
            return new Tuple2<>(value1.f0, value1.f1 + value2.f1);
        }
    }

    // ------------------------------------------------------------------------------------------
    // 可序列化数据生成器
    private static class DataGeneratorSource implements org.apache.flink.streaming.api.functions.source.SourceFunction<Tuple2<Long, Long>>, Serializable {

        private final long numElements;
        private final long numKeys;
        private volatile boolean running = true;

        public DataGeneratorSource(long numElements, long numKeys) {
            this.numElements = numElements;
            this.numKeys = numKeys;
        }

        @Override
        public void run(SourceContext<Tuple2<Long, Long>> ctx) throws Exception {
            long counter = 0;
            long startTime = System.currentTimeMillis();
            while (running && counter < numElements) {
                ctx.collect(new Tuple2<>(counter % numKeys, 1L));
                counter++;

                // 每 1M 条输出一次耗时
                if (counter % 1000000 == 0) {
                    long now = System.currentTimeMillis();
                    System.out.println(Thread.currentThread() + ": Took " + (now - startTime) + " ms for 1M elements");
                    startTime = now;
                }
            }
        }

        @Override
        public void cancel() {
            running = false;
        }
    }
}
