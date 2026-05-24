package auction.messages;

public enum MessageType {
    AUCTION_START,       // Seller → Buyers: auction begins, item info + opening price
    BID,                 // Buyer → Seller: buyer places a bid
    NEW_HIGHEST_BID,     // Seller → Buyers: broadcast current highest bid
    NO_BID,              // Buyer → Seller: buyer passes this round
    AUCTION_END,         // Seller → Buyers: auction is over
    SOLD,                // Seller → Winner: item sold
    NOT_SOLD             // Seller → All: reserve price not met
}
