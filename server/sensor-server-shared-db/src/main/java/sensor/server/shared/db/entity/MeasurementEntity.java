package sensor.server.shared.db.entity;

import java.time.LocalDateTime;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.FetchType;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.Index;
import javax.persistence.JoinColumn;
import javax.persistence.ManyToOne;
import javax.persistence.Table;

import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import lombok.ToString;
import sensor.server.shared.model.Measurement;
import sensor.server.shared.model.MeasurementType;

@Data
@NoArgsConstructor
@RequiredArgsConstructor
@EqualsAndHashCode(exclude = { "type", "value", "timing", "device" })
@ToString(exclude = { "type", "value", "timing", "device" })
@Entity
@Table(indexes = { @Index(columnList = "deviceId,type,timing") })
public class MeasurementEntity {

	@Id
	@GeneratedValue(strategy = GenerationType.AUTO)
	private Integer id;

	@Column(nullable = false)
	private @NonNull MeasurementType type;

	@Column(nullable = false)
	private @NonNull Double value;

	@Column(nullable = false)
	private @NonNull LocalDateTime timing;

	@ManyToOne(fetch = FetchType.LAZY, optional = false)
	@JoinColumn(name = "deviceId")
	private @NonNull DeviceEntity device;

	public static MeasurementEntity of(Measurement measurement, DeviceEntity device) {
		return new MeasurementEntity(measurement.getType(), measurement.getValue(), measurement.getTiming(), device);
	}

	public Measurement toMeasurement() {
		return Measurement.builder().type(this.getType()).value(this.getValue()).timing(this.getTiming()).build();
	}

}
