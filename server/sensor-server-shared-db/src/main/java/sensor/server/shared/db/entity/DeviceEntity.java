package sensor.server.shared.db.entity;

import java.util.List;

import javax.persistence.CascadeType;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.FetchType;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.OneToMany;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import lombok.ToString;

@Data
@NoArgsConstructor
@RequiredArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(exclude = { "fullUniqueIdentifier", "measurements" })
@ToString(exclude = { "fullUniqueIdentifier", "measurements" })
@Entity
public class DeviceEntity {

	@Id
	@GeneratedValue(strategy = GenerationType.AUTO)
	private Integer id;

	@Column(unique = true)
	private @NonNull String fullUniqueIdentifier;

	@OneToMany(mappedBy = "device", fetch = FetchType.EAGER, cascade = CascadeType.ALL)
	private List<MeasurementEntity> measurements;

	public static DeviceEntity of(String fullUniqueIdentifier) {
		return new DeviceEntity(fullUniqueIdentifier);
	}

}
