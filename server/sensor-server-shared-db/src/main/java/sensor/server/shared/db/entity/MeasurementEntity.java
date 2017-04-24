package sensor.server.shared.db.entity;

import java.time.LocalDateTime;

import javax.persistence.Entity;
import javax.persistence.FetchType;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.JoinColumn;
import javax.persistence.ManyToOne;

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
public class MeasurementEntity {

	@Id
	@GeneratedValue(strategy = GenerationType.AUTO)
	private Integer id;

	private @NonNull MeasurementType type;

	private @NonNull Double value;

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
