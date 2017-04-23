package sensor.server.receive.service;

import java.util.Set;

import sensor.server.shared.model.DeviceMeasurements;

public interface ReceivedDataProcessingService {
	public void process(Set<DeviceMeasurements> measurements);
}
