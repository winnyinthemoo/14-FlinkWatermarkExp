package com.hazel.watermark;

import org.apache.flink.api.common.functions.RuntimeContext;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.streaming.api.functions.source.RichParallelSourceFunction;

/**
 * Old-style DataGeneratorSource which accepts a GeneratorFunction instead of java.util.function.Function.
 */
public class DataGeneratorSource<T> extends RichParallelSourceFunction<T> {

    private final GeneratorFunction<Long, T> generatorFunction;
    private final long totalElements;
    private final TypeInformation<T> typeInfo;
    private volatile boolean running = true;

    public DataGeneratorSource(
            GeneratorFunction<Long, T> generatorFunction,
            long totalElements,
            TypeInformation<T> typeInfo) {

        this.generatorFunction = generatorFunction;
        this.totalElements = totalElements;
        this.typeInfo = typeInfo;
    }

    @Override
    public void run(SourceContext<T> ctx) throws Exception {
        RuntimeContext rc = getRuntimeContext();
        int subtaskIdx = rc.getIndexOfThisSubtask();
        int parallelism = rc.getNumberOfParallelSubtasks();

        // Average distribution of ids
        long start = subtaskIdx * (totalElements / parallelism);
        long end = (subtaskIdx + 1) * (totalElements / parallelism);

        // open()
        generatorFunction.open(null);

        for (long i = start; i < end && running; i++) {
            T value = generatorFunction.map(i);
            synchronized (ctx.getCheckpointLock()) {
                ctx.collect(value);
            }
        }

        generatorFunction.close();
    }

    @Override
    public void cancel() {
        running = false;
    }

    public TypeInformation<T> getProducedType() {
        return typeInfo;
    }
}
