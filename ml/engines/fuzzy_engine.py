import numpy as np

try:
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
    SKFUZZY_AVAILABLE = True
except ImportError:
    SKFUZZY_AVAILABLE = False
    print("Warning: scikit-fuzzy not available, using weighted average fallback")


class FuzzyWellnessEngine:

    def __init__(self):
        self.fuzzy_available = SKFUZZY_AVAILABLE
        if self.fuzzy_available:
            try:
                self._build_fuzzy_system()
            except Exception as e:
                print(f"Fuzzy system build error: {e}")
                self.fuzzy_available = False

    def _build_fuzzy_system(self):
        universe = np.arange(0, 101, 1)

        self.linguistic = ctrl.Antecedent(universe, 'linguistic')
        self.consumption = ctrl.Antecedent(universe, 'consumption')
        self.behavioral = ctrl.Antecedent(universe, 'behavioral')
        self.wellness = ctrl.Consequent(universe, 'wellness')

        for var in [self.linguistic, self.consumption, self.behavioral]:
            var['low']    = fuzz.trimf(var.universe, [0,  0,  40])
            var['medium'] = fuzz.trimf(var.universe, [25, 50, 75])
            var['high']   = fuzz.trimf(var.universe, [60, 100, 100])

        self.wellness['critical']  = fuzz.trimf(self.wellness.universe, [0,  0,  25])
        self.wellness['poor']      = fuzz.trimf(self.wellness.universe, [15, 30, 45])
        self.wellness['moderate']  = fuzz.trimf(self.wellness.universe, [35, 50, 65])
        self.wellness['good']      = fuzz.trimf(self.wellness.universe, [55, 70, 85])
        self.wellness['excellent'] = fuzz.trimf(self.wellness.universe, [75, 100, 100])

        L = self.linguistic
        C = self.consumption
        B = self.behavioral
        W = self.wellness

        rules = [
            ctrl.Rule(L['low'] & C['low'] & B['low'], W['critical']),
            ctrl.Rule(L['low'] & C['low'],             W['poor']),
            ctrl.Rule(L['low'] & B['low'],             W['poor']),
            ctrl.Rule(L['low'] & C['medium'],          W['poor']),
            ctrl.Rule(C['low'] & B['low'],             W['poor']),
            ctrl.Rule(L['medium'] & C['low'] & B['low'], W['poor']),
            ctrl.Rule(L['medium'] & C['medium'] & B['medium'], W['moderate']),
            ctrl.Rule(L['low'] & C['high'],            W['moderate']),
            ctrl.Rule(L['medium'] & B['medium'],       W['moderate']),
            ctrl.Rule(L['high'] & C['low'],            W['moderate']),
            ctrl.Rule(L['medium'] & C['medium'],       W['moderate']),
            ctrl.Rule(L['high'] & C['medium'] & B['medium'], W['good']),
            ctrl.Rule(L['medium'] & C['high'] & B['high'],   W['good']),
            ctrl.Rule(L['high'] & B['high'],           W['good']),
            ctrl.Rule(C['high'] & B['high'],           W['good']),
            ctrl.Rule(L['medium'] & C['high'],         W['good']),
            ctrl.Rule(B['high'] & L['medium'],         W['good']),
            ctrl.Rule(L['medium'] & C['medium'] & B['high'], W['good']),
            ctrl.Rule(L['high'] & C['high'] & B['high'],   W['excellent']),
            ctrl.Rule(L['high'] & C['high'] & B['medium'], W['excellent']),
        ]

        wellness_ctrl = ctrl.ControlSystem(rules)
        self.wellness_sim = ctrl.ControlSystemSimulation(wellness_ctrl)

    def compute_wellness(
        self,
        linguistic_score: float,
        consumption_score: float,
        behavioral_score: float,
    ) -> dict:
        l = max(0.1, min(99.9, float(linguistic_score)))
        c = max(0.1, min(99.9, float(consumption_score)))
        b = max(0.1, min(99.9, float(behavioral_score)))

        if self.fuzzy_available:
            try:
                self.wellness_sim.input['linguistic']  = l
                self.wellness_sim.input['consumption'] = c
                self.wellness_sim.input['behavioral']  = b
                self.wellness_sim.compute()
                wellness_score = float(self.wellness_sim.output['wellness'])
            except Exception as e:
                print(f"Fuzzy compute error: {e}, using fallback")
                wellness_score = self._weighted_fallback(l, c, b)
        else:
            wellness_score = self._weighted_fallback(l, c, b)

        wellness_score = max(0, min(100, wellness_score))
        risk_level = self._get_risk_level(wellness_score)
        dominant = self._get_dominant_factor(l, c, b)
        explanation = self._get_explanation(l, c, b, wellness_score)

        return {
            'wellness_score': round(wellness_score, 1),
            'risk_level': risk_level,
            'input_scores': {
                'linguistic': round(l, 1),
                'consumption': round(c, 1),
                'behavioral': round(b, 1),
            },
            'dominant_factor': dominant,
            'explanation': explanation,
            'method': 'fuzzy_mamdani' if self.fuzzy_available else 'weighted_average',
        }

    def _weighted_fallback(self, l: float, c: float, b: float) -> float:
        return (l * 0.40) + (c * 0.35) + (b * 0.25)

    def _get_risk_level(self, score: float) -> str:
        if score >= 80: return 'excellent'
        if score >= 65: return 'good'
        if score >= 45: return 'moderate'
        if score >= 30: return 'poor'
        return 'critical'

    def _get_dominant_factor(self, l: float, c: float, b: float) -> str:
        factors = {'linguistic': l, 'consumption': c, 'behavioral': b}
        return min(factors, key=factors.get)

    def _get_explanation(self, l: float, c: float, b: float, w: float) -> str:
        dominant = self._get_dominant_factor(l, c, b)
        level = self._get_risk_level(w)

        intros = {
            'excellent': "Your wellness indicators are looking great!",
            'good': "Your overall wellness is in a good place.",
            'moderate': "Your wellness is moderate — some areas need attention.",
            'poor': "Your wellness indicators suggest you may be struggling.",
            'critical': "Your wellness signals need immediate attention.",
        }

        factor_advice = {
            'linguistic': "Your emotional expression patterns are the main area to focus on — try journaling or talking to someone.",
            'consumption': "Your content consumption is pulling your score down — consider watching more uplifting content.",
            'behavioral': "Your behavioral patterns (late-night activity, irregular routines) are affecting your wellness — try improving your sleep schedule.",
        }

        return f"{intros[level]} {factor_advice[dominant]}"
