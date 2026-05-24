package auction.messages;

import java.io.Serializable;

public class Message implements Serializable {
    private final MessageType type;
    private final String senderId;
    private final String receiverId;   // null = broadcast
    private final double price;
    private final String itemName;
    private final String content;

    // Full constructor
    public Message(MessageType type, String senderId, String receiverId,
                   double price, String itemName, String content) {
        this.type       = type;
        this.senderId   = senderId;
        this.receiverId = receiverId;
        this.price      = price;
        this.itemName   = itemName;
        this.content    = content;
    }

    // Convenience: no item name
    public Message(MessageType type, String senderId, String receiverId,
                   double price, String content) {
        this(type, senderId, receiverId, price, null, content);
    }

    // Convenience: no price / item
    public Message(MessageType type, String senderId, String receiverId, String content) {
        this(type, senderId, receiverId, 0, null, content);
    }

    public MessageType getType()      { return type; }
    public String      getSenderId()  { return senderId; }
    public String      getReceiverId(){ return receiverId; }
    public double      getPrice()     { return price; }
    public String      getItemName()  { return itemName; }
    public String      getContent()   { return content; }

    @Override
    public String toString() {
        return String.format("[%s] %s → %s | price=%.2f | %s",
                type, senderId,
                receiverId == null ? "ALL" : receiverId,
                price,
                content != null ? content : "");
    }
}
