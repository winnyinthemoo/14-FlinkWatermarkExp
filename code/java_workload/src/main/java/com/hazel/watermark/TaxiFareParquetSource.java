package com.hazel.watermark;

import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.parquet.hadoop.ParquetReader;
import org.apache.parquet.avro.AvroParquetReader;

import org.apache.avro.generic.GenericRecord;
import org.apache.hadoop.fs.Path;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.PriorityQueue;

public class TaxiFareParquetSource implements SourceFunction<TaxiFare> {

    private final String parquetPath;
    private final long watermarkDelayMs;
    private static final int BATCH_SIZE = 5;
    private volatile boolean running = true;

    public TaxiFareParquetSource(String parquetPath,long WatermarkDelayMs) {
        this.parquetPath = parquetPath;
        this.watermarkDelayMs = WatermarkDelayMs;
    }

    @Override
    public void run(SourceContext<TaxiFare> ctx) throws Exception {

        ParquetReader<GenericRecord> reader = AvroParquetReader
                .<GenericRecord>builder(new Path(parquetPath))
                .build();

        GenericRecord record;
        long rideId = 0;
        long maxStartTime = 0;

        while (running && (record = reader.read())!=null) {

            // NYC Taxi schema: tpep_pickup_datetime / tpep_dropoff_datetime
            // 假设字段是 long 类型（微秒时间戳）
            long pickupMills = ((Number) record.get("tpep_pickup_datetime")).longValue()/1000;
            long dropoffMills = ((Number) record.get("tpep_dropoff_datetime")).longValue()/1000;
            long vendor_id=((Number) record.get("VendorID")).longValue();
            long tip=((Number) record.get("tip_amount")).longValue();
            long fare=((Number) record.get("total_amount")).longValue();

            // 转换为毫秒（Instant.ofEpochMilli 需要毫秒）
            Instant pickupTime = Instant.ofEpochMilli(pickupMills);
            Instant dropoffTime = Instant.ofEpochMilli(dropoffMills);

            // 1) Emit START event
            TaxiFare startEvent = new TaxiFare(
                    Long.toString(rideId),
                    Long.toString(vendor_id),
                    pickupTime,
                    tip,
                    fare
            );
            ctx.collect(startEvent);
//            long wm = pickupTime.toEpochMilli() - watermarkDelayMs;
//            if (wm < 0) {
//                wm = 0;
//            }
//            ctx.collectWithTimestamp(startEvent, pickupTime.toEpochMilli());
//            ctx.emitWatermark(new Watermark(wm));
//            //startEvents.add(startEvent);
            maxStartTime = Math.max(maxStartTime, startEvent.getEventTimeMillis());

            // 2) Emit END eventctx.collect(endEvent);
            rideId++;
            if(rideId % 10 == 0) {
                Thread.sleep(10);
            }
            // Thread.sleep(5);
        }
    }

    @Override
    public void cancel() {
        running = false;
    }
}
