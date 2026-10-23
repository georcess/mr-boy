<?php
/**
 * Sales Summary Page
 * 
 * Standalone report showing daily, monthly, and yearly sales.
 */
require_once __DIR__ . '/../../models/Order.php';

$summary = Order::getSalesSummary();
?>
<!DOCTYPE html>
<html>
<head>
    <title>Mr. Boy Sales Report</title>
    <style>
        body { font-family: sans-serif; background: #f6f1ec; padding: 50px; text-align: center; }
        .box { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: inline-block; }
        h1 { color: #4b2e2e; }
        .price { font-size: 24px; color: #e04300; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h1>Sales Report 📊</h1>
        <p>Today's Sales: <span class="price">₱<?php echo number_format($summary['today'], 2); ?></span></p>
        <hr>
        <p>This Month: <span class="price">₱<?php echo number_format($summary['month'], 2); ?></span></p>
        <hr>
        <p>This Year: <span class="price">₱<?php echo number_format($summary['year'], 2); ?></span></p>
    </div>
</body>
</html>
