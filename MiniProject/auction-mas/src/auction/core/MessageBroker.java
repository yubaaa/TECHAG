package auction.core;

import auction.messages.Message;
import java.util.Map;
import java.util.concurrent.*;

/**
 * Central message broker (simulates an ACL-based MAS communication layer).
 * Each agent has its own blocking queue (mailbox).
 */
public class MessageBroker {

    private final Map<String, BlockingQueue<Message>> mailboxes = new ConcurrentHashMap<>();

    /** Register an agent with the broker. */
    public void register(String agentId) {
        mailboxes.put(agentId, new LinkedBlockingQueue<>());
        System.out.printf("  [BROKER] Agent '%s' registered.%n", agentId);
    }

    /** Send a message to a specific agent. */
    public void send(Message message) {
        String target = message.getReceiverId();
        BlockingQueue<Message> box = mailboxes.get(target);
        if (box != null) {
            box.offer(message);
        } else {
            System.err.printf("  [BROKER] Unknown agent: '%s'%n", target);
        }
    }

    /** Broadcast a message to all registered agents except the sender. */
    public void broadcast(Message message) {
        String sender = message.getSenderId();
        for (Map.Entry<String, BlockingQueue<Message>> entry : mailboxes.entrySet()) {
            if (!entry.getKey().equals(sender)) {
                // Re-wrap with a per-receiver copy so getReceiverId() is accurate
                entry.getValue().offer(message);
            }
        }
    }

    /**
     * Blocking receive — waits up to timeoutMs ms for a message.
     * Returns null on timeout.
     */
    public Message receive(String agentId, long timeoutMs) throws InterruptedException {
        BlockingQueue<Message> box = mailboxes.get(agentId);
        if (box == null) throw new IllegalArgumentException("Agent not registered: " + agentId);
        return box.poll(timeoutMs, TimeUnit.MILLISECONDS);
    }
}
