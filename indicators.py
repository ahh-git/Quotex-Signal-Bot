# indicators.py
import pandas as pd
import pandas_ta as ta

class TechnicalAnalyzer:
    def __init__(self, df):
        self.df = df

    def calculate_all(self):
        """Runs all major indicators used by professional scalpers."""
        if self.df is None or len(self.df) < 50:
            return self.df

        # 1. Trend Indicators
        self.df['EMA_50'] = ta.ema(self.df['Close'], length=50)
        self.df['EMA_200'] = ta.ema(self.df['Close'], length=200)
        
        # ADX Calculation with safety check
        try:
            adx = ta.adx(self.df['High'], self.df['Low'], self.df['Close'], length=14)
            if adx is not None and not adx.empty:
                self.df['ADX'] = adx['ADX_14']
            else:
                self.df['ADX'] = 0
        except:
            self.df['ADX'] = 0

        # 2. Momentum Indicators
        self.df['RSI'] = ta.rsi(self.df['Close'], length=14)
        
        # Stochastic Oscillator (Key for binary options timing)
        stoch = ta.stoch(self.df['High'], self.df['Low'], self.df['Close'])
        self.df = pd.concat([self.df, stoch], axis=1) # Adds STOCHk_14_3_3 and STOCHd_14_3_3

        # --- THE FIX IS HERE ---
        # 3. Volatility (Bollinger Bands)
        # We calculate it separately and rename columns to avoid the "BBL_20_2.0" naming error
        bb = ta.bbands(self.df['Close'], length=20, std=2)
        
        # bbands returns 5 columns usually. The first is Lower, Third is Upper.
        # We explicitly map them to simple names.
        if bb is not None:
            self.df['LowerBB'] = bb.iloc[:, 0]  # The Lower Band
            self.df['UpperBB'] = bb.iloc[:, 2]  # The Upper Band
        
        return self.df

    def get_signal_strength(self, row):
        """
        Returns a signal dictionary with weighted confidence.
        """
        score = 0
        reasons = []
        signal_type = "NEUTRAL"
        
        # Safety Check for NaN values before processing logic
        if pd.isna(row.get('RSI')) or pd.isna(row.get('LowerBB')):
            return {
                "signal": "WAIT",
                "confidence": 0,
                "reasons": ["Initializing data..."],
                "score": 0
            }
        
        # --- LOGIC MATRIX ---
        
        # 1. RSI Logic (Weight: 2)
        if row['RSI'] < 30:
            score += 2
            reasons.append("RSI Oversold (Reversal Likely)")
        elif row['RSI'] > 70:
            score -= 2
            reasons.append("RSI Overbought (Reversal Likely)")

        # 2. Bollinger Band Rejection (Weight: 3)
        # UPDATED to use the new simple names 'LowerBB' and 'UpperBB'
        if row['Close'] <= row['LowerBB']:
            score += 3
            reasons.append("Price pierced Lower Bollinger Band")
        elif row['Close'] >= row['UpperBB']:
            score -= 3
            reasons.append("Price pierced Upper Bollinger Band")

        # 3. Stochastic Crossover (Weight: 2)
        # Check if columns exist first
        if 'STOCHk_14_3_3' in row and 'STOCHd_14_3_3' in row:
            k = row['STOCHk_14_3_3']
            d = row['STOCHd_14_3_3']
            if k < 20 and k > d: # Golden Cross in oversold
                score += 2
                reasons.append("Stochastic Bullish Crossover")
            elif k > 80 and k < d: # Death Cross in overbought
                score -= 2
                reasons.append("Stochastic Bearish Crossover")

        # 4. Trend Filter (ADX)
        if row.get('ADX', 0) > 25:
            reasons.append("Strong Trend Identified (ADX > 25)")
        else:
            reasons.append("Weak Trend / Ranging Market")

        # --- FINAL DECISION ---
        confidence = abs(score) * 10 # Scale roughly to percentage
        confidence = min(confidence + 50, 98) # Base 50%, max 98%

        if score >= 4:
            signal_type = "CALL (UP)"
        elif score <= -4:
            signal_type = "PUT (DOWN)"
        else:
            signal_type = "WAIT"
            confidence = 0

        return {
            "signal": signal_type,
            "confidence": confidence,
            "reasons": reasons,
            "score": score
        }
