package sensor.server.web.service.db;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import lombok.NonNull;
import sensor.server.shared.db.entity.DeviceEntity;
import sensor.server.shared.db.entity.MeasurementEntity;
import sensor.server.shared.db.service.DeviceDbService;
import sensor.server.shared.db.service.MeasurementDbService;
import sensor.server.shared.model.Measurement;
import sensor.server.shared.model.MeasurementType;
import sensor.server.web.model.DeviceNotFoundException;
import sensor.server.web.service.MeasurementDataService;

@Service
public class MeasurementDataDbService implements MeasurementDataService {

	private static final Logger LOGGER = LoggerFactory.getLogger(MeasurementDataDbService.class);

	private DeviceDbService deviceDbService;
	private MeasurementDbService measurementDbService;

	@Autowired
	public MeasurementDataDbService(@NonNull DeviceDbService deviceDbService,
			MeasurementDbService measurementDbService) {
		this.deviceDbService = deviceDbService;
		this.measurementDbService = measurementDbService;
	}

	@Override
	public List<Measurement> listByDeviceId(String deviceId, List<MeasurementType> typeFilter) {
		LOGGER.debug("Querying database for device {} and filter {}", deviceId, typeFilter);
		List<MeasurementEntity> deviceMeasurements;
		if (typeFilter == null || typeFilter.isEmpty()) {
			deviceMeasurements = listAllByDeviceId(deviceId);
		} else {
			deviceMeasurements = measurementDbService.listByDeviceId(deviceId, typeFilter);
		}
		List<Measurement> measurements = deviceMeasurements.stream().map(measurementEntity -> {
			return measurementEntity.toMeasurement();
		}).collect(Collectors.toList());
		LOGGER.debug("Found measurements {}", measurements);
		return measurements;
	}

	private List<MeasurementEntity> listAllByDeviceId(String deviceId) {
		DeviceEntity device = deviceDbService.readByFullUniqueIdentifier(deviceId);
		if (device == null) {
			LOGGER.debug("Device not found");
			throw new DeviceNotFoundException("The device could not be found.");
		}
		if (device.getMeasurements() == null) {
			LOGGER.debug("No measurements");
			return new ArrayList<>();
		}
		return device.getMeasurements();
	}

}
