package auction.agents;

import auction.core.MessageBroker;
import auction.messages.Message;

/**
 * Base class for all agents in the MAS.
 * Each agent runs in its own thread.
 */
public abstract class Agent implements Runnable {

    protected final String        id;
    protected final MessageBroker broker;
    protected volatile boolean    running = true;

    protected static final long MSG_TIMEOUT_MS = 5_000;   // wait up to 5 s for a message

    public Agent(String id, MessageBroker broker) {
        this.id     = id;
        this.broker = broker;
        broker.register(id);
    }

    public String getId() { return id; }

    /** Convenience wrapper for broker send. */
    protected void send(Message msg) {
        broker.send(msg);
    }

    /** Convenience wrapper for broker broadcast. */
    protected void broadcast(Message msg) {
        broker.broadcast(msg);
    }

    /** Blocking receive from this agent's mailbox. */
    protected Message receive() throws InterruptedException {
        return broker.receive(id, MSG_TIMEOUT_MS);
    }

    /** Each subclass implements its own behaviour loop. */
    @Override
    public abstract void run();
}
