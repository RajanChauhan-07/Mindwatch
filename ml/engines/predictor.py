from datetime import datetime, timedelta
from typing import Optional

try:
    from prophet import Prophet
    import pandas as pd
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False


class WellnessPredictor:

    def predict(self, historical_scores: list) -> dict:
        if not historical_scores or len(historical_scores) < 7:
            return {
                'available': False,
                'reason': f'Need at least 7 days of data (have {len(historical_scores)})',
                'predictions': [],
            }

        if not PROPHET_AVAILABLE:
            return self._simple_forecast(historical_scores)

        try:
            return self._prophet_forecast(historical_scores)
        except Exception as e:
            print(f"Prophet error: {e}")
            return self._simple_forecast(historical_scores)

    def _prophet_forecast(self, historical_scores: list) -> dict:
        import pandas as pd

        df = pd.DataFrame(historical_scores)
        df.columns = ['ds', 'y']
        df['ds'] = pd.to_datetime(df['ds'])
        df = df.dropna()

        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
        )
        model.fit(df)

        future = model.make_future_dataframe(periods=7)
        forecast = model.predict(future)
        future_forecast = forecast.tail(7)

        last_score = df['y'].iloc[-1]
        first_forecast = future_forecast['yhat'].iloc[0]
        trend = 'improving' if first_forecast > last_score + 2 else \
                'declining' if first_forecast < last_score - 2 else 'stable'

        predictions = []
        for _, row in future_forecast.iterrows():
            score = max(0, min(100, float(row['yhat'])))
            lower = max(0, min(100, float(row['yhat_lower'])))
            upper = max(0, min(100, float(row['yhat_upper'])))
            predictions.append({
                'date': row['ds'].strftime('%Y-%m-%d'),
                'predicted_score': round(score, 1),
                'lower_bound': round(lower, 1),
                'upper_bound': round(upper, 1),
                'trend': trend,
            })

        return {
            'available': True,
            'predictions': predictions,
            'overall_trend': trend,
            'confidence': 'high' if len(historical_scores) >= 30 else
                          'medium' if len(historical_scores) >= 14 else 'low',
            'data_points_used': len(historical_scores),
            'method': 'prophet',
        }

    def _simple_forecast(self, historical_scores: list) -> dict:
        scores = [s['score'] for s in historical_scores[-7:]]
        avg = sum(scores) / len(scores)
        recent_avg = sum(scores[-3:]) / 3
        trend = 'improving' if recent_avg > avg + 2 else \
                'declining' if recent_avg < avg - 2 else 'stable'

        predictions = []
        base_date = datetime.now()
        for i in range(1, 8):
            date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            noise = (i * 0.5) if trend == 'improving' else \
                    (-i * 0.5) if trend == 'declining' else 0
            predicted = max(0, min(100, recent_avg + noise))
            predictions.append({
                'date': date,
                'predicted_score': round(predicted, 1),
                'lower_bound': round(max(0, predicted - 10), 1),
                'upper_bound': round(min(100, predicted + 10), 1),
                'trend': trend,
            })

        return {
            'available': True,
            'predictions': predictions,
            'overall_trend': trend,
            'confidence': 'low',
            'data_points_used': len(historical_scores),
            'method': 'simple_moving_average',
        }
