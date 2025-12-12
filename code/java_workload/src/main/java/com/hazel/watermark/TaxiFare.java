package com.hazel.watermark;

import org.apache.flink.annotation.VisibleForTesting;
import org.apache.flink.streaming.runtime.streamrecord.StreamRecord;

import java.io.Serializable;
import java.time.Instant;
import java.util.Objects;

public class TaxiFare implements Serializable {

//    /** Default constructor */
//    public TaxiFare() {
//        this.startTime = Instant.now();
//    }

    /** Constructor used for CSV parsing */
    public TaxiFare(
            String rideId,
            String taxiId,
            Instant startTime,
            float tip,
            float totalFare) {

        this.rideId = rideId;
        this.taxiId = taxiId;
        this.startTime = startTime;
        this.tip = tip;
        this.totalFare = totalFare;
    }

    public String rideId;      // changed to String
    public String taxiId;      // changed to String
    public Instant startTime;
    public float tip;
    public float totalFare;

    public String getTaxiId() {
        return taxiId;
    }

    @Override
    public String toString() {
        return rideId
                + "," + taxiId
                + "," + startTime.toString()
                + "," + tip
                + "," + totalFare;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        TaxiFare taxiFare = (TaxiFare) o;
        return Float.compare(taxiFare.tip, tip) == 0
                && Float.compare(taxiFare.totalFare, totalFare) == 0
                && Objects.equals(rideId, taxiFare.rideId)
                && Objects.equals(taxiId, taxiFare.taxiId)
                && Objects.equals(startTime, taxiFare.startTime);
    }

    @Override
    public int hashCode() {
        return Objects.hash(rideId, taxiId, startTime, tip, totalFare);
    }

    /** Event time for watermarks */
    public long getEventTimeMillis() {
        return startTime.toEpochMilli();
    }

    @VisibleForTesting
    public StreamRecord<TaxiFare> asStreamRecord() {
        return new StreamRecord<>(this, this.getEventTimeMillis());
    }
}
