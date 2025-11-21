"""Flask HTTP API server for KnowledgeBaseBuilderAgent."""

from flask import Flask, request, jsonify
from agents.workers.knowledge_base_builder_agent import KnowledgeBaseBuilderAgent
from shared.utils import setup_logger
import json
import sys

logger = setup_logger(__name__)
app = Flask(__name__)

agent = KnowledgeBaseBuilderAgent(
    agent_id="KnowledgeBaseBuilderAgent",
    supervisor_id="SupervisorAgent_Main"
)

logger.info("KnowledgeBaseBuilderAgent API server initialized")


class MessageCapture:
    """Capture agent messages for API responses."""
    def __init__(self):
        self.last_message = None
    
    def capture(self, message_dict):
        """Store the last message sent by the agent."""
        self.last_message = message_dict


message_capture = MessageCapture()


@app.route('/message', methods=['POST'])
def handle_message():
    """Handle incoming JSON messages from supervisor or other agents.
    
    Returns: JSON message (completion_report, health_check_response, or error_report)
    """
    try:
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json"
            }), 400
        
        json_data = request.get_json()
        json_string = json.dumps(json_data)
        
        logger.info(f"Received message: {json_data.get('type', 'unknown')} from {json_data.get('sender', 'unknown')}")
        
        original_send = agent._send_json_message
        agent._send_json_message = message_capture.capture
        
        agent.handle_incoming_message(json_string)
        
        agent._send_json_message = original_send
        
        if message_capture.last_message:
            response_message = message_capture.last_message
            message_capture.last_message = None
            return jsonify(response_message), 200
        else:
            return jsonify({
                "error": "No response generated"
            }), 500
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request: {str(e)}")
        return jsonify({
            "error": "Invalid JSON format",
            "details": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint. Returns JSON status response."""
    try:
        health_check_message = {
            "message_id": "health-check-api",
            "sender": "API_Server",
            "recipient": "KnowledgeBaseBuilderAgent",
            "type": "health_check",
            "timestamp": agent._get_current_timestamp()
        }
        
        original_send = agent._send_json_message
        agent._send_json_message = message_capture.capture
        
        agent.handle_incoming_message(json.dumps(health_check_message))
        
        agent._send_json_message = original_send
        
        if message_capture.last_message:
            response = message_capture.last_message
            message_capture.last_message = None
            return jsonify(response), 200
        else:
            return jsonify({
                "status": "I'm up and ready",
                "agent_id": agent.agent_id
            }), 200
            
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Health check failed",
            "details": str(e)
        }), 500


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information."""
    return jsonify({
        "service": "KnowledgeBaseBuilderAgent API",
        "version": "0.1.0",
        "endpoints": {
            "POST /message": "Handle incoming JSON messages",
            "GET /health": "Health check endpoint"
        }
    }), 200


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    host = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'
    
    logger.info(f"Starting API server on {host}:{port}")
    app.run(host=host, port=port, debug=False)

