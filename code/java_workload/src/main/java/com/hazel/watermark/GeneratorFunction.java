package com.hazel.watermark;

import org.apache.flink.annotation.Experimental;
import org.apache.flink.api.common.functions.RuntimeContext;

/**
 * Old-API compatible GeneratorFunction.
 *
 * Compatible with all Flink versions <= 1.13.
 *
 * @param <T> input type (normally Long index)
 * @param <O> output type (generated event)
 */
@Experimental
public interface GeneratorFunction<T, O> {

    /**
     * Initialization method for the function.
     * Called once before processing begins.
     */
    default void open(RuntimeContext context) throws Exception {}

    /**
     * Tear-down method for the function.
     */
    default void close() throws Exception {}

    /**
     * Map one input value to an output value.
     */
    O map(T value) throws Exception;
}
