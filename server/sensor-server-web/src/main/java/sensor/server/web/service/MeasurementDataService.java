package sensor.server.web.service;

import java.util.List;

import sensor.server.shared.model.Measurement;
import sensor.server.shared.model.MeasurementType;

public interface MeasurementDataService {

	public List<Measurement> listByDeviceId(String deviceId, List<MeasurementType> typeFilter);

}
