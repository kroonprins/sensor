package sensor.server.shared.model;

import java.io.Serializable;
import java.util.List;

import lombok.Data;

@Data
public class DeviceMeasurements implements Serializable {
	private static final long serialVersionUID = -2648282275899890385L;

	private String deviceId;
	private List<Measurement> measurements;

}
