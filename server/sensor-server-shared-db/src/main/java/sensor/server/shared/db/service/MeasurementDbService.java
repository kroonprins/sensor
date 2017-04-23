package sensor.server.shared.db.service;

import org.springframework.data.repository.CrudRepository;

import sensor.server.shared.db.entity.MeasurementEntity;

public interface MeasurementDbService extends CrudRepository<MeasurementEntity, Integer> {

}
