package sensor.server.process.service;

import sensor.server.shared.model.DeviceMeasurements;

public interface ProcessDataService {

	public void process(DeviceMeasurements deviceMeasurements);
}
