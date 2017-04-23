package sensor.server.receive.service.activemq;

import java.util.Set;

import javax.jms.Topic;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jms.core.JmsMessagingTemplate;
import org.springframework.stereotype.Service;

import lombok.NonNull;
import sensor.server.receive.service.ReceivedDataProcessingService;
import sensor.server.shared.model.DeviceMeasurements;

@Service
public class ReceivedDataToActiveMqService implements ReceivedDataProcessingService {

	private static final Logger LOGGER = LoggerFactory.getLogger(ReceivedDataToActiveMqService.class);

	private JmsMessagingTemplate jmsMessagingTemplate;
	private Topic topic;

	@Autowired
	public ReceivedDataToActiveMqService(@NonNull JmsMessagingTemplate jmsMessagingTemplate, @NonNull Topic topic) {
		LOGGER.debug("Creating service for publishing measurements to active mq - {} - {}", jmsMessagingTemplate,
				topic);
		this.jmsMessagingTemplate = jmsMessagingTemplate;
		this.topic = topic;
	}

	@Override
	public void process(@NonNull Set<DeviceMeasurements> deviceMeasurements) {
		LOGGER.info("Publish measurements to active mq");
		LOGGER.debug("Active MQ topic {}", topic);
		deviceMeasurements.forEach(measurement -> jmsMessagingTemplate.convertAndSend(topic, measurement));
	}

}
