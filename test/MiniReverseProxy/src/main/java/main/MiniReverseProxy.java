package main;

import javax.servlet.http.HttpServletRequest;

import org.eclipse.jetty.client.api.Request;
import org.eclipse.jetty.proxy.AsyncProxyServlet;
import org.eclipse.jetty.server.HttpConfiguration;
import org.eclipse.jetty.server.HttpConnectionFactory;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.ServerConnector;
import org.eclipse.jetty.server.handler.HandlerCollection;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;

public class MiniReverseProxy extends AsyncProxyServlet {

	static final long serialVersionUID = 1L;

	public static void main(String[] args) throws Exception {

		Server server = new Server();

		HttpConfiguration httpConfig = new HttpConfiguration();
		HttpConnectionFactory connectionFactory = new HttpConnectionFactory(httpConfig);

		ServerConnector http = new ServerConnector(server, connectionFactory);
		http.setPort(8901);
		server.addConnector(http);

		HandlerCollection handlers = new HandlerCollection();
		server.setHandler(handlers);
		ServletContextHandler context = new ServletContextHandler(handlers, "/", ServletContextHandler.SESSIONS);

		MiniReverseProxy.HttpTransparent proxy = new MiniReverseProxy.HttpTransparent();
		ServletHolder holderPortalProxy = new ServletHolder("MiniReverseProxy", proxy);
		holderPortalProxy.setName("HttpsToHttpsReverseProxy");
		holderPortalProxy.setInitParameter("proxyTo", "http://192.168.42.1:8080");
		holderPortalProxy.setInitParameter("prefix", "/");
		holderPortalProxy.setAsyncSupported(true);
		context.addServlet(holderPortalProxy, "/*");

		server.start();
		server.join();
	}

	public static class HttpTransparent extends AsyncProxyServlet.Transparent {

		private static final long serialVersionUID = 1L;

		@Override
		protected void addProxyHeaders(HttpServletRequest clientRequest, Request proxyRequest) {
			// Don't let the proxy add headers
		}
	}

}
