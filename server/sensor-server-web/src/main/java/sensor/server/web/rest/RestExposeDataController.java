package sensor.server.web.rest;

import java.util.List;
import java.util.stream.Collectors;

import javax.servlet.http.HttpServletRequest;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import lombok.NonNull;
import sensor.server.shared.model.Measurement;
import sensor.server.shared.model.MeasurementType;
import sensor.server.web.service.MeasurementDataService;

@RestController
@RequestMapping("/sensors")
public class RestExposeDataController {

	private static final Logger LOGGER = LoggerFactory.getLogger(RestExposeDataController.class);

	private MeasurementDataService measurementDataService;

	@Autowired
	public RestExposeDataController(MeasurementDataService measurementDataService) {
		this.measurementDataService = measurementDataService;
	}

	@GetMapping(path = "ping")
	public String ping() {
		return "ok";
	}

	@GetMapping(path = "/{deviceId}")
	public List<Measurement> measurementsByDeviceId(@NonNull @PathVariable(value = "deviceId") String deviceId,
			@RequestParam(value = "type", required = false) /* Optional< */List<String>/* > */ typeFilter,
			HttpServletRequest request) {
		LOGGER.info("{} - {} - Received request for all measurements of device {} and type filter {}",
				request.getRemoteAddr(), request.getHeader("X-FORWARDED-FOR"), deviceId, typeFilter);
		// Bug in library: when using Optional the Optional<List<String>> never
		// gets more than one element in the List
		// List<MeasurementType> measurementTypeFilter = typeFilter.map(list ->
		// {
		// return list.stream().map(type -> {
		// return MeasurementType.valueOf(type);
		// }).collect(Collectors.toList());
		// }).orElse(null);
		List<MeasurementType> measurementTypeFilter = null;
		if (typeFilter != null) {
			measurementTypeFilter = typeFilter.stream().map(type -> {
				return MeasurementType.valueOf(type);
			}).collect(Collectors.toList());
		}
		return this.measurementDataService.listByDeviceId(deviceId, measurementTypeFilter);
	}
}