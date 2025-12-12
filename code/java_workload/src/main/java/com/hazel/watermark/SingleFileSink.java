package com.hazel.watermark;

import org.apache.flink.configuration.Configuration;
import org.apache.flink.core.fs.FileSystem;
import org.apache.flink.core.fs.Path;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;

import java.io.OutputStream;

public class SingleFileSink<T> extends RichSinkFunction<T> {

    private final String outputPath;
    private transient OutputStream out;

    public SingleFileSink(String outputPath) {
        this.outputPath = outputPath;
    }

    @Override
    public void open(Configuration parameters) throws Exception {
        Path path = new Path(outputPath);
        FileSystem fs = path.getFileSystem();
        // 如果文件已存在，覆盖写
        out = fs.create(path, FileSystem.WriteMode.OVERWRITE);
    }

    @Override
    public void invoke(T value, Context context) throws Exception {
        if (value != null) {
            String line = value.toString() + "\n";
            out.write(line.getBytes());
        }
    }

    @Override
    public void close() throws Exception {
        if (out != null) {
            out.flush();
            out.close();
        }
    }
}
