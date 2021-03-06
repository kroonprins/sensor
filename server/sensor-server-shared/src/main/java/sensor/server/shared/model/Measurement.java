package sensor.server.shared.model;

import java.io.Serializable;
import java.time.LocalDateTime;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@NoArgsConstructor
@AllArgsConstructor
@Data
@Builder
public class Measurement implements Serializable {
	private static final long serialVersionUID = 8046351952506241631L;

	private MeasurementType type;
	private Double value;
	private LocalDateTime timing;
}
