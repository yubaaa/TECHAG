package auction.agents;

import auction.core.MessageBroker;
import auction.messages.Message;
import auction.messages.MessageType;

import java.util.*;

/**
 * Seller Agent — manages the full English-auction lifecycle:
 *  1. Announce item + opening price
 *  2. Collect bids for a round
 *  3. Broadcast highest bid
 *  4. Repeat until no new bids or time limit
 *  5. Compare final price with reserve → SOLD / NOT_SOLD
 */
public class SellerAgent extends Agent {

    private final String       itemName;
    private final double       openingPrice;
    private final double       reservePrice;   // secret floor
    private final double       minIncrement;   // minimum raise per round
    private final int          maxRounds;
    private final long         roundDurationMs;
    private final List<String> buyerIds;

    private double  currentHighestBid;
    private String  currentWinner = null;

    public SellerAgent(String id,
                       MessageBroker broker,
                       String itemName,
                       double openingPrice,
                       double reservePrice,
                       double minIncrement,
                       int maxRounds,
                       long roundDurationMs,
                       List<String> buyerIds) {
        super(id, broker);
        this.itemName        = itemName;
        this.openingPrice    = openingPrice;
        this.reservePrice    = reservePrice;
        this.minIncrement    = minIncrement;
        this.maxRounds       = maxRounds;
        this.roundDurationMs = roundDurationMs;
        this.buyerIds        = Collections.unmodifiableList(buyerIds);
        this.currentHighestBid = openingPrice;
    }

    @Override
    public void run() {
        System.out.printf("%n═══════════════════════════════════════════════════%n");
        System.out.printf("  AUCTION STARTED by %s%n", id);
        System.out.printf("  Item        : %s%n", itemName);
        System.out.printf("  Opening price : $%.2f%n", openingPrice);
        System.out.printf("  Reserve price : [HIDDEN]%n");
        System.out.printf("  Buyers        : %s%n", buyerIds);
        System.out.printf("  Max rounds    : %d%n", maxRounds);
        System.out.printf("═══════════════════════════════════════════════════%n%n");

        // ── Step 1: Broadcast auction start ──────────────────────────
        Message startMsg = new Message(
                MessageType.AUCTION_START, id, null,
                openingPrice, itemName,
                String.format("Auction started for '%s'. Opening price: $%.2f. Min increment: $%.2f",
                        itemName, openingPrice, minIncrement));
        broadcast(startMsg);

        // ── Auction rounds ────────────────────────────────────────────
        Set<String> activeBuyers = new HashSet<>(buyerIds);

        for (int round = 1; round <= maxRounds && !activeBuyers.isEmpty(); round++) {
            System.out.printf("%n─── ROUND %d ─────────────────────────────────────────%n", round);
            System.out.printf("  Current price : $%.2f  |  Leader: %s%n",
                    currentHighestBid, currentWinner == null ? "none" : currentWinner);

            // Collect bids from all active buyers within the round window
            Map<String, Double> roundBids = collectBids(activeBuyers);

            // Determine best bid of this round
            double  bestRoundBid    = currentHighestBid;
            String  bestRoundBidder = currentWinner;

            for (Map.Entry<String, Double> entry : roundBids.entrySet()) {
                double bid = entry.getValue();
                if (bid > bestRoundBid) {
                    bestRoundBid    = bid;
                    bestRoundBidder = entry.getKey();
                }
            }

            // Remove buyers who passed this round
            Set<String> passed = new HashSet<>(activeBuyers);
            passed.removeAll(roundBids.keySet());
            activeBuyers.removeAll(passed);

            if (!passed.isEmpty()) {
                System.out.printf("  Buyers who passed: %s%n", passed);
            }

            // Was there any new valid bid?
            if (bestRoundBid > currentHighestBid) {
                currentHighestBid = bestRoundBid;
                currentWinner     = bestRoundBidder;
                System.out.printf("  ★ New highest bid: $%.2f by %s%n",
                        currentHighestBid, currentWinner);

                // Broadcast new highest bid to all still-active buyers
                if (!activeBuyers.isEmpty()) {
                    Message newHighest = new Message(
                            MessageType.NEW_HIGHEST_BID, id, null,
                            currentHighestBid, itemName,
                            String.format("New highest bid: $%.2f by %s. Min next bid: $%.2f",
                                    currentHighestBid, currentWinner,
                                    currentHighestBid + minIncrement));
                    broadcast(newHighest);
                }
            } else {
                System.out.printf("  No new bids this round. Active buyers remaining: %d%n",
                        activeBuyers.size());
                // If nobody bid, remaining active buyers also stop
                activeBuyers.clear();
            }
        }

        // ── Auction end ───────────────────────────────────────────────
        System.out.printf("%n═══════════════════════════════════════════════════%n");
        System.out.printf("  AUCTION ENDED%n");

        // Notify all buyers
        Message endMsg = new Message(MessageType.AUCTION_END, id, null,
                currentHighestBid, itemName, "The auction has ended.");
        broadcast(endMsg);

        // Small pause to let end message be processed
        sleep(300);

        if (currentWinner != null && currentHighestBid >= reservePrice) {
            System.out.printf("  SOLD! '%s' → %s for $%.2f%n", itemName, currentWinner, currentHighestBid);
            System.out.printf("  (Reserve was $%.2f — reserve met ✔)%n", reservePrice);

            // Notify winner
            send(new Message(MessageType.SOLD, id, currentWinner, currentHighestBid, itemName,
                    String.format("Congratulations! You won '%s' for $%.2f", itemName, currentHighestBid)));

            // Notify losers
            for (String buyer : buyerIds) {
                if (!buyer.equals(currentWinner)) {
                    send(new Message(MessageType.NOT_SOLD, id, buyer, currentHighestBid, itemName,
                            String.format("Auction over. '%s' sold to %s for $%.2f.",
                                    itemName, currentWinner, currentHighestBid)));
                }
            }
        } else {
            System.out.printf("  NOT SOLD. Highest bid $%.2f did not meet reserve $%.2f ✘%n",
                    currentHighestBid, reservePrice);

            for (String buyer : buyerIds) {
                send(new Message(MessageType.NOT_SOLD, id, buyer, currentHighestBid, itemName,
                        String.format("Auction over. Reserve price not met. '%s' was not sold.", itemName)));
            }
        }

        System.out.printf("═══════════════════════════════════════════════════%n");
        running = false;
    }

    /**
     * Open a bid-collection window.
     * Returns a map of buyerId → bid for every buyer who bid (not passed) this round.
     */
    private Map<String, Double> collectBids(Set<String> activeBuyers) {
        Map<String, Double> bids    = new HashMap<>();
        Set<String>         waiting = new HashSet<>(activeBuyers);

        long deadline = System.currentTimeMillis() + roundDurationMs;

        while (!waiting.isEmpty() && System.currentTimeMillis() < deadline) {
            long remaining = deadline - System.currentTimeMillis();
            if (remaining <= 0) break;

            Message msg;
            try {
                msg = broker.receive(id, remaining);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }

            if (msg == null) break;   // timeout

            String sender = msg.getSenderId();
            if (!activeBuyers.contains(sender)) continue;  // ignore unknown

            if (msg.getType() == MessageType.BID) {
                double bid = msg.getPrice();
                if (bid >= currentHighestBid + minIncrement) {
                    bids.put(sender, bid);
                    System.out.printf("    [BID received] %s → $%.2f%n", sender, bid);
                } else {
                    System.out.printf("    [BID REJECTED] %s bid $%.2f (below min $%.2f)%n",
                            sender, bid, currentHighestBid + minIncrement);
                }
                waiting.remove(sender);

            } else if (msg.getType() == MessageType.NO_BID) {
                System.out.printf("    [PASS] %s passes this round%n", sender);
                waiting.remove(sender);
            }
        }

        // Any buyer still in 'waiting' timed out → treat as pass
        if (!waiting.isEmpty()) {
            System.out.printf("    [TIMEOUT] No response from: %s — treated as pass%n", waiting);
        }

        return bids;
    }

    private void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}
