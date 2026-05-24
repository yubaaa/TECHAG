package auction.core;

import auction.agents.BuyerAgent;
import auction.agents.SellerAgent;

import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * AuctionSystem — bootstrap class.
 *
 * Creates the broker, instantiates all agents, starts them as threads,
 * and waits for the auction to complete.
 */
public class AuctionSystem {

    public static void main(String[] args) throws InterruptedException {

        System.out.println("╔═══════════════════════════════════════════════════╗");
        System.out.println("║      MULTI-AGENT AUCTION SYSTEM  (MAS)            ║");
        System.out.println("║      English Auction — 1 Seller / N Buyers        ║");
        System.out.println("╚═══════════════════════════════════════════════════╝");
        System.out.println();

        // ── Shared message broker ─────────────────────────────────────
        MessageBroker broker = new MessageBroker();

        // ── Auction parameters ────────────────────────────────────────
        String itemName        = "Vintage Rolex Submariner";
        double openingPrice    = 500.0;
        double reservePrice    = 800.0;   // secret floor (only the seller knows)
        double minIncrement    = 10.0;    // minimum raise per round
        int    maxRounds       = 6;
        long   roundDurationMs = 2_000;   // 2 seconds per round

        // ── Buyer definitions  (id, budget, aggressiveness, rng-seed) ─
        List<String> buyerIds = Arrays.asList("Buyer-Alice", "Buyer-Bob", "Buyer-Carol");

        // ── Instantiate agents ────────────────────────────────────────
        // NOTE: Seller must be instantiated AFTER buyers so all buyers
        //       are registered with the broker before the seller broadcasts.
        BuyerAgent alice = new BuyerAgent("Buyer-Alice", broker, "Seller-1",
                /*budget*/  950.0, /*aggressiveness*/ 0.80, /*seed*/ 42L);

        BuyerAgent bob   = new BuyerAgent("Buyer-Bob",   broker, "Seller-1",
                /*budget*/  780.0, /*aggressiveness*/ 0.55, /*seed*/ 7L);

        BuyerAgent carol = new BuyerAgent("Buyer-Carol", broker, "Seller-1",
                /*budget*/ 1100.0, /*aggressiveness*/ 0.65, /*seed*/ 99L);

        SellerAgent seller = new SellerAgent(
                "Seller-1", broker,
                itemName, openingPrice, reservePrice,
                minIncrement, maxRounds, roundDurationMs,
                buyerIds);

        // ── Thread pool ───────────────────────────────────────────────
        ExecutorService pool = Executors.newFixedThreadPool(4);

        // Start buyer threads first so they are ready to receive
        pool.submit(alice);
        pool.submit(bob);
        pool.submit(carol);

        // Small delay to ensure buyers are in their receive() loop
        Thread.sleep(200);

        // Start seller — kicks off the auction
        pool.submit(seller);

        // ── Wait for completion ───────────────────────────────────────
        pool.shutdown();
        boolean finished = pool.awaitTermination(60, TimeUnit.SECONDS);

        System.out.println();
        if (finished) {
            System.out.println("All agents have terminated. Auction system shutting down.");
        } else {
            System.out.println("Timeout — forcing shutdown.");
            pool.shutdownNow();
        }
    }
}
