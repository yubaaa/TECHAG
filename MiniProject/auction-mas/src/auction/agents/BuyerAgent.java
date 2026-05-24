package auction.agents;

import auction.core.MessageBroker;
import auction.messages.Message;
import auction.messages.MessageType;

import java.util.Random;

/**
 * Buyer Agent — autonomous bidder with a private budget cap.
 *
 * Strategy:
 *  - Each buyer has a maximum budget they will never exceed.
 *  - When the current price is below their budget, they bid with a random
 *    increment above the minimum raise.
 *  - They become more aggressive (larger increment) when the price is still
 *    well below their budget, and more conservative when close to their limit.
 *  - Once the price exceeds their budget they permanently stop bidding.
 */
public class BuyerAgent extends Agent {

    private final String sellerId;
    private final double budget;          // private maximum willingness to pay
    private final double aggressiveness;  // 0.0–1.0; higher → bigger increments
    private final Random rng;

    private double  currentKnownPrice = 0;
    private boolean auctionActive     = true;
    private boolean wonItem           = false;

    public BuyerAgent(String id,
                      MessageBroker broker,
                      String sellerId,
                      double budget,
                      double aggressiveness,
                      long seed) {
        super(id, broker);
        this.sellerId      = sellerId;
        this.budget        = budget;
        this.aggressiveness = Math.max(0.0, Math.min(1.0, aggressiveness));
        this.rng           = new Random(seed);
    }

    @Override
    public void run() {
        System.out.printf("  [%s] Ready. Budget=$%.2f, Aggressiveness=%.0f%%%n",
                id, budget, aggressiveness * 100);

        while (auctionActive) {
            Message msg;
            try {
                msg = receive();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }

            if (msg == null) continue;   // timeout, keep waiting

            handleMessage(msg);
        }

        System.out.printf("  [%s] Shutting down. %s%n", id,
                wonItem ? "★ WON the auction!" : "Did not win.");
    }

    private void handleMessage(Message msg) {
        switch (msg.getType()) {

            case AUCTION_START:
                currentKnownPrice = msg.getPrice();
                System.out.printf("%n  [%s] Auction started! Item='%s' Opening=$%.2f%n",
                        id, msg.getItemName(), currentKnownPrice);
                decideAndBid(msg.getItemName());
                break;

            case NEW_HIGHEST_BID:
                currentKnownPrice = msg.getPrice();
                System.out.printf("  [%s] Informed: highest bid now $%.2f%n",
                        id, currentKnownPrice);
                decideAndBid(msg.getItemName());
                break;

            case AUCTION_END:
                System.out.printf("  [%s] Received AUCTION_END.%n", id);
                auctionActive = false;
                break;

            case SOLD:
                System.out.printf("  [%s] ★ I WON '%s' for $%.2f!%n",
                        id, msg.getItemName(), msg.getPrice());
                wonItem       = true;
                auctionActive = false;
                break;

            case NOT_SOLD:
                System.out.printf("  [%s] %s%n", id, msg.getContent());
                auctionActive = false;
                break;

            default:
                // ignore unexpected messages
        }
    }

    /**
     * Decide whether to bid or pass, then send the appropriate message to the seller.
     */
    private void decideAndBid(String itemName) {
        // Base minimum next bid (seller enforces this, we respect it)
        // We estimate it as currentPrice + small increment
        double minNextBid = currentKnownPrice + 1.0;

        if (minNextBid > budget) {
            System.out.printf("  [%s] Price $%.2f exceeds budget $%.2f → PASS%n",
                    id, currentKnownPrice, budget);
            send(new Message(MessageType.NO_BID, id, sellerId,
                    currentKnownPrice, "Budget exceeded, passing."));
            return;
        }

        // Compute headroom and decide probabilistically
        double headroom    = budget - currentKnownPrice;
        double bidChance   = 0.5 + aggressiveness * 0.4;   // 50–90%

        if (rng.nextDouble() > bidChance) {
            System.out.printf("  [%s] Choosing to PASS this round (strategic).%n", id);
            send(new Message(MessageType.NO_BID, id, sellerId,
                    currentKnownPrice, "Strategic pass."));
            return;
        }

        // Choose increment: aggressive = larger share of headroom
        double maxExtra  = headroom * (0.1 + aggressiveness * 0.3);
        double extra     = 1.0 + rng.nextDouble() * maxExtra;
        double myBid     = Math.min(currentKnownPrice + extra, budget);

        // Round to 2 decimal places
        myBid = Math.round(myBid * 100.0) / 100.0;

        System.out.printf("  [%s] Bidding $%.2f (budget left: $%.2f)%n",
                id, myBid, budget - myBid);
        send(new Message(MessageType.BID, id, sellerId, myBid, itemName,
                String.format("%s bids $%.2f", id, myBid)));
    }
}
