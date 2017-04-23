package sensor.server.shared.db.service;

import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;

import sensor.server.shared.db.entity.DeviceEntity;

public interface DeviceDbService extends CrudRepository<DeviceEntity, Integer> {

	public DeviceEntity readByFullUniqueIdentifier(String fullUniqueIdentifier);

	@Query("select e.id from DeviceEntity e where fullUniqueIdentifier = ?1")
	public Integer readIdForFullUniqueIdentifier(String fullUniqueIdentifier);

}
