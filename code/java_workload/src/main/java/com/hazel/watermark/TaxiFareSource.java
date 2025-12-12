package com.hazel.watermark;

import org.apache.flink.streaming.api.functions.source.SourceFunction;

import java.io.BufferedReader;
import java.io.FileReader;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

public class TaxiFareSource implements SourceFunction<TaxiFare> {

    private final String csvPath;
    private volatile boolean running = true;

    public TaxiFareSource(String csvPath) {
        this.csvPath = csvPath;
    }

    @Override
    public void run(SourceContext<TaxiFare> ctx) throws Exception {

        try (BufferedReader br = new BufferedReader(new FileReader(csvPath))) {

            String header = br.readLine();  // 跳过表头
            if (header == null) {
                return;
            }

            String line;
            while (running && (line = br.readLine()) != null) {

                String[] parts = line.split(",", -1);
                if (parts.length < 6) {
                    continue; // 跳过脏数据
                }

                String tripId = parts[0];
                String taxiId = parts[1];

                Instant startTs = parseTimestamp(parts[2]);
                // Instant endTs = parseTimestamp(parts[3]); // 可以不用
                float tips = parseAmount(parts[4]);
                float fare = parseAmount(parts[5]);


                TaxiFare fareObj = new TaxiFare(
                        tripId,
                        taxiId,
                        startTs,
                        tips,
                        fare
                );

                synchronized (ctx.getCheckpointLock()) {
                    ctx.collect(fareObj);
                }

                Thread.sleep(50);
            }
        }
    }

    /**
     * 解析日期时间字符串，例如：
     * "11/01/2025 12:00:00 AM"
     */
    private Instant parseTimestamp(String ts) {
        ts = ts.replace("\"", "").trim();

        DateTimeFormatter formatter =
                DateTimeFormatter.ofPattern("MM/dd/yyyy hh:mm:ss a", Locale.US);

        LocalDateTime ldt = LocalDateTime.parse(ts, formatter);

        // 将 local time 直接作为 UTC 时间
        return ldt.toInstant(ZoneOffset.UTC);
    }


    private float parseAmount(String s) {
        s = s.replace("\"", "").replace("$", "").trim();
        if (s.isEmpty()) {
            return 0f; // 空字符串当 0 处理
        }
        return Float.parseFloat(s);
    }



    @Override
    public void cancel() {
        running = false;
    }
}
