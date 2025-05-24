# Crypto Trader Agent Setup Guide

## Overview

The Crypto Trader agent ("Quantum") is designed for cryptocurrency market analysis and trading. For security and liability reasons, the actual trading implementation is kept private, but we provide a comprehensive example template.

## Architecture

```
CryptoTrader (Quantum)
├── Market Analysis
│   ├── Price Monitoring
│   ├── Technical Indicators
│   └── Pattern Recognition
├── Strategy Engine
│   ├── Momentum Trading
│   ├── Mean Reversion
│   ├── Scalping
│   └── DCA (Dollar Cost Averaging)
├── Risk Management
│   ├── Position Sizing
│   ├── Stop Loss/Take Profit
│   └── Portfolio Limits
└── Execution
    ├── Paper Trading
    └── Live Trading (Implement Yourself)
```

## Setting Up Your Own Crypto Trader

### 1. Copy the Example Template

```bash
cp agents/crypto_trader.example.py agents/crypto_trader.py
```

### 2. Implement Exchange Integration

Choose your exchange(s) and implement the API integration:

```python
# Example with ccxt library
import ccxt

class CryptoTrader(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        
        # Initialize exchange
        self.exchange = ccxt.binance({
            'apiKey': os.getenv('EXCHANGE_API_KEY'),
            'secret': os.getenv('EXCHANGE_SECRET'),
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
```

### 3. Implement Market Analysis

```python
async def analyze_market(self, symbol: str) -> Dict[str, Any]:
    # Fetch OHLCV data
    ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=100)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Calculate indicators
    df['rsi'] = ta.RSI(df['close'])
    df['macd'], df['signal'], df['histogram'] = ta.MACD(df['close'])
    df['bb_upper'], df['bb_middle'], df['bb_lower'] = ta.BBANDS(df['close'])
    
    # Determine trend
    sma_20 = df['close'].rolling(20).mean()
    sma_50 = df['close'].rolling(50).mean()
    trend = 'bullish' if sma_20.iloc[-1] > sma_50.iloc[-1] else 'bearish'
    
    return {
        'symbol': symbol,
        'price': df['close'].iloc[-1],
        'rsi': df['rsi'].iloc[-1],
        'macd': df['macd'].iloc[-1],
        'trend': trend,
        'volume_24h': df['volume'].sum(),
        'volatility': df['close'].pct_change().std()
    }
```

### 4. Implement Trading Strategies

```python
def momentum_strategy(self, analysis: Dict) -> Optional[TradeSignal]:
    """Example momentum strategy"""
    if (analysis['trend'] == 'bullish' and 
        analysis['rsi'] > 50 and analysis['rsi'] < 70 and
        analysis['macd'] > analysis['signal']):
        
        return TradeSignal(
            action='buy',
            confidence=0.8,
            entry_price=analysis['price'],
            stop_loss=analysis['price'] * 0.98,
            take_profit=[
                analysis['price'] * 1.02,
                analysis['price'] * 1.05
            ]
        )
    return None
```

### 5. Risk Management Configuration

```python
# In your config
risk_config = {
    'max_position_size': 0.1,  # 10% of portfolio per position
    'max_daily_loss': 0.05,    # 5% daily loss limit
    'max_open_positions': 5,
    'risk_per_trade': 0.02,    # 2% risk per trade
    'use_trailing_stop': True,
    'trailing_stop_percent': 0.03
}
```

## Security Best Practices

### 1. API Key Management

```python
# Use environment variables
EXCHANGE_API_KEY=your_key_here
EXCHANGE_SECRET=your_secret_here

# Never commit keys to git
echo "*.env" >> .gitignore
```

### 2. Rate Limiting

```python
# Implement rate limiting
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=10, period=60)  # 10 calls per minute
async def fetch_price(self, symbol):
    return self.exchange.fetch_ticker(symbol)
```

### 3. Error Handling

```python
async def safe_trade_execution(self, signal):
    try:
        # Validate signal
        if not self.validate_signal(signal):
            return {'error': 'Invalid signal'}
        
        # Check risk limits
        if not self.check_risk_limits(signal):
            return {'error': 'Risk limit exceeded'}
        
        # Execute trade
        result = await self.execute_trade(signal)
        
        # Log for audit
        self.log_trade(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Trade execution failed: {e}")
        return {'error': str(e)}
```

## Testing Strategy

### 1. Paper Trading First

Always start with paper trading:

```python
# Force paper trading for new strategies
if self.is_new_strategy():
    self.config.paper_trading = True
    self.config.paper_trading_duration = timedelta(days=30)
```

### 2. Backtesting

```python
async def backtest_strategy(self, strategy, start_date, end_date):
    """Run historical backtest"""
    historical_data = await self.fetch_historical_data(start_date, end_date)
    
    results = {
        'trades': [],
        'profit_loss': 0,
        'win_rate': 0,
        'max_drawdown': 0
    }
    
    for candle in historical_data:
        signal = strategy.analyze(candle)
        if signal:
            results['trades'].append(self.simulate_trade(signal))
    
    return self.calculate_metrics(results)
```

### 3. Performance Monitoring

```python
def get_performance_metrics(self):
    return {
        'total_return': self.calculate_total_return(),
        'sharpe_ratio': self.calculate_sharpe_ratio(),
        'max_drawdown': self.calculate_max_drawdown(),
        'win_rate': self.calculate_win_rate(),
        'profit_factor': self.calculate_profit_factor(),
        'average_win': self.calculate_average_win(),
        'average_loss': self.calculate_average_loss()
    }
```

## Common Pitfalls to Avoid

1. **Over-leveraging**: Never use more than 2-3x leverage
2. **No Stop Loss**: Always set stop losses
3. **Emotional Trading**: Let the algorithm decide
4. **Poor Risk Management**: Never risk more than you can afford to lose
5. **Ignoring Fees**: Account for trading fees in calculations
6. **Market Manipulation**: Be aware of pump and dump schemes
7. **Technical Failures**: Have fallback systems

## Recommended Libraries

```python
# requirements.txt additions
ccxt>=4.0.0          # Exchange connectivity
pandas>=2.0.0        # Data analysis
ta-lib>=0.4.0        # Technical indicators
numpy>=1.24.0        # Numerical computing
backtrader>=1.9.0    # Backtesting framework
plotly>=5.0.0        # Charting
redis>=4.0.0         # For caching market data
```

## Legal Disclaimer

**IMPORTANT**: 
- Cryptocurrency trading involves substantial risk of loss
- Past performance does not guarantee future results
- This is not financial advice
- Always do your own research
- Never invest more than you can afford to lose
- The developers are not responsible for any trading losses
- Comply with all local regulations and tax obligations

## Support

For questions about the example implementation (not trading advice):
- Review the `crypto_trader.example.py` file
- Check the test cases in `tests/test_crypto_trader.py`
- Join our Discord community (no financial advice given)

Remember: **Start with paper trading, test thoroughly, and trade responsibly!**