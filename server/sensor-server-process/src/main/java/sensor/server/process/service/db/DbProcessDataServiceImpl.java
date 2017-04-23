package sensor.server.process.service.db;

import java.util.ArrayList;
import java.util.List;

import javax.transaction.Transactional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import lombok.NonNull;
import sensor.server.shared.db.entity.DeviceEntity;
import sensor.server.shared.db.entity.MeasurementEntity;
import sensor.server.shared.db.service.DeviceDbService;
import sensor.server.shared.model.DeviceMeasurements;
import sensor.server.shared.model.Measurement;

@Service
@Transactional
public class DbProcessDataServiceImpl implements DbProcessDataService {
	private static final Logger LOGGER = LoggerFactory.getLogger(DbProcessDataServiceImpl.class);

	private DeviceDbService deviceDbService;
	// private MeasurementDbService measurementDbService;

	@Autowired
	public DbProcessDataServiceImpl(@NonNull DeviceDbService deviceDbService/*
																			 * , @NonNull
																			 * MeasurementDbService
																			 * measurementDbService
																			 */) {
		this.deviceDbService = deviceDbService;
		// this.measurementDbService = measurementDbService;
	}

	@Override
	public void process(DeviceMeasurements deviceMeasurements) {
		// Integer deviceEntityId =
		// deviceDbService.readIdForFullUniqueIdentifier(deviceMeasurements.getDeviceId());
		// DeviceEntity deviceEntity;
		// if (deviceEntityId == null) {
		// deviceEntity =
		// deviceDbService.save(DeviceEntity.of(deviceMeasurements.getDeviceId()));
		// } else {
		// deviceEntity = new DeviceEntity(deviceEntityId,
		// deviceMeasurements.getDeviceId(), null);
		// }
		// for (Measurement measurement : deviceMeasurements.getMeasurements())
		// {
		// measurementDbService.save(MeasurementEntity.of(measurement,
		// deviceEntity));
		// }
		LOGGER.info("Writing measurements to database");
		LOGGER.debug("Measurements: {}", deviceMeasurements);

		List<MeasurementEntity> measurementEntities = new ArrayList<>();

		// Retrieving the ID only to avoid all the measurements to be fetched
		// with it (and don't want to use LAZY fetching because EAGER makes
		// more sense for all other cases)
		Integer deviceEntityId = deviceDbService.readIdForFullUniqueIdentifier(deviceMeasurements.getDeviceId());

		DeviceEntity deviceEntity = new DeviceEntity(deviceEntityId, deviceMeasurements.getDeviceId(),
				measurementEntities);

		// Add measurements to device (will automatically be persisted by the
		// cascade)
		for (Measurement measurement : deviceMeasurements.getMeasurements()) {
			measurementEntities.add(MeasurementEntity.of(measurement, deviceEntity));
		}

		deviceDbService.save(deviceEntity);
	}

}
