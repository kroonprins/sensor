package sensor.server.shared.db.service;

import java.util.List;

import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;

import sensor.server.shared.db.entity.MeasurementEntity;
import sensor.server.shared.model.MeasurementType;

public interface MeasurementDbService extends CrudRepository<MeasurementEntity, Integer> {

	@Query("select m from MeasurementEntity m inner join m.device d where d.fullUniqueIdentifier = ?1 and m.type in (?2) order by type,timing")
	public List<MeasurementEntity> listByDeviceId(String deviceId, List<MeasurementType> typeFilter);
}
