package sensor.server.receive.web.rest;

import java.util.Set;

import javax.servlet.http.HttpServletRequest;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import sensor.server.receive.service.ReceivedDataProcessingService;
import sensor.server.shared.model.DeviceMeasurements;

@RestController
@RequestMapping("/sensor")
public class RestReceiveDataController {

	private static final Logger LOGGER = LoggerFactory.getLogger(RestReceiveDataController.class);

	private ReceivedDataProcessingService receivedDataProcessingService;

	@Autowired
	public RestReceiveDataController(ReceivedDataProcessingService receivedDataProcessingService) {
		this.receivedDataProcessingService = receivedDataProcessingService;
	}

	@GetMapping(path = "ping")
	public String ping() {
		return "ok";
	}

	@PostMapping(path = "measurement")
	public void receive(@RequestBody Set<DeviceMeasurements> deviceMeasurements, HttpServletRequest request) {
		LOGGER.info("{} - {} - Received measurements {}", request.getRemoteAddr(), request.getHeader("X-FORWARDED-FOR"),
				deviceMeasurements);
		this.receivedDataProcessingService.process(deviceMeasurements);
	}
}