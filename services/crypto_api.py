"""
Servicio para consultar precios de criptomonedas y tasas de cambio en tiempo real.
Con almacenamiento en caché y contingencia multi-fuente en cascada:
1. CoinGecko API (fuente primaria global)
2. Binance Public Ticker API (fuente secundaria de alta velocidad)
3. Coinpaprika API (fuente terciaria para altcoins como KAS, ALPH)
4. Contingencia (fallbacks) offline calibrada
"""

import json
import urllib.request
from typing import Dict, Any, Tuple

DEFAULT_PRICES = {
    "bitcoin": {"usd": 81000.0, "symbol": "BTC", "name": "Bitcoin"},
    "litecoin": {"usd": 65.0, "symbol": "LTC", "name": "Litecoin"},
    "dogecoin": {"usd": 0.085, "symbol": "DOGE", "name": "Dogecoin"},
    "kaspa": {"usd": 0.045, "symbol": "KAS", "name": "Kaspa"},
    "alephium": {"usd": 0.080, "symbol": "ALPH", "name": "Alephium"},
    "ravencoin": {"usd": 0.0016, "symbol": "RVN", "name": "Ravencoin"},
    "ethereum-classic": {"usd": 12.0, "symbol": "ETC", "name": "Ethereum Classic"},
    "zcash": {"usd": 1190.0, "symbol": "ZEC", "name": "Zcash"},
    "minotari": {"usd": 0.0012, "symbol": "XTM", "name": "Tari"},
    "monero": {"usd": 600.0, "symbol": "XMR", "name": "Monero"},
    "helium": {"usd": 0.41, "symbol": "HNT", "name": "Helium"},
    "bitcoin-cash": {"usd": 430.0, "symbol": "BCH", "name": "Bitcoin Cash"}
}

DEFAULT_USD_PEN = 3.75


def _fetch_from_coingecko() -> Dict[str, float]:
    ids = "bitcoin,litecoin,dogecoin,kaspa,alephium,ravencoin,ethereum-classic,zcash,minotari,monero,helium,bitcoin-cash"
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "CryptoSimulatorPeru/2.0 (Streamlit App)"}
    )
    with urllib.request.urlopen(req, timeout=3.5) as response:
        data = json.loads(response.read().decode())
        result = {}
        for coin_id in DEFAULT_PRICES:
            if coin_id in data and "usd" in data[coin_id]:
                result[coin_id] = float(data[coin_id]["usd"])
        if len(result) >= 5:
            return result
    raise ValueError("CoinGecko data incomplete")


def _fetch_from_binance() -> Dict[str, float]:
    binance_map = {
        "BTCUSDT": "bitcoin",
        "LTCUSDT": "litecoin",
        "DOGEUSDT": "dogecoin",
        "ETCUSDT": "ethereum-classic",
        "RVNUSDT": "ravencoin",
        "ZECUSDT": "zcash",
        "BCHUSDT": "bitcoin-cash",
        "HNTUSDT": "helium"
    }
    url = "https://api.binance.com/api/v3/ticker/price"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "CryptoSimulatorPeru/2.0"}
    )
    with urllib.request.urlopen(req, timeout=3.0) as response:
        data = json.loads(response.read().decode())
        result = {}
        for item in data:
            sym = item.get("symbol", "")
            if sym in binance_map:
                result[binance_map[sym]] = float(item.get("price", 0))
        if len(result) >= 4:
            return result
    raise ValueError("Binance data incomplete")


def _fetch_from_coinpaprika() -> Dict[str, float]:
    paprika_coins = {
        "kas-kaspa": "kaspa",
        "alph-alephium": "alephium"
    }
    result = {}
    for pid, cid in paprika_coins.items():
        try:
            url = f"https://api.coinpaprika.com/v1/tickers/{pid}"
            req = urllib.request.Request(url, headers={"User-Agent": "CryptoSimulatorPeru/2.0"})
            with urllib.request.urlopen(req, timeout=2.5) as r:
                data = json.loads(r.read().decode())
                p = float(data.get("quotes", {}).get("USD", {}).get("price", 0))
                if p > 0:
                    result[cid] = p
        except Exception:
            pass
    return result


def fetch_live_prices(return_source: bool = False) -> Any:
    """
    Obtiene los precios actuales en USD mediante contingencia multi-fuente en cascada:
    1. CoinGecko API
    2. Binance API + Coinpaprika API
    3. Fallback Offline predeterminado
    """
    prices = {k: v["usd"] for k, v in DEFAULT_PRICES.items()}
    source = "Fallback Offline"
    is_live = False

    # 1. Intentar CoinGecko
    try:
        cg_prices = _fetch_from_coingecko()
        for k, v in cg_prices.items():
            prices[k] = v
        is_live = True
        source = "CoinGecko API"
    except Exception:
        # 2. Fallback a Binance + Coinpaprika
        try:
            bn_prices = _fetch_from_binance()
            for k, v in bn_prices.items():
                prices[k] = v
            # Complementar altcoins que no están en Binance con Coinpaprika
            pap_prices = _fetch_from_coinpaprika()
            for k, v in pap_prices.items():
                prices[k] = v
            is_live = True
            source = "Binance + Coinpaprika (Alta Velocidad)"
        except Exception:
            # 3. Mantener precios default offline
            is_live = False
            source = "Valores de Referencia Offline"

    if return_source:
        return prices, is_live, source
    return prices, is_live


def fetch_usd_to_pen() -> Tuple[float, bool]:
    """
    Obtiene el tipo de cambio oficial USD a PEN (Sol Peruano) con fallback secundario.
    """
    # 1. Open Exchange Rates API pública
    url_primary = "https://open.er-api.com/v6/latest/USD"
    try:
        req = urllib.request.Request(
            url_primary,
            headers={"User-Agent": "CryptoSimulatorPeru/2.0"}
        )
        with urllib.request.urlopen(req, timeout=3.5) as response:
            data = json.loads(response.read().decode())
            rate = float(data.get("rates", {}).get("PEN", 0))
            if rate > 2.5:
                return round(rate, 3), True
    except Exception:
        pass

    # 2. ExchangeRate-API pública secundaria
    url_secondary = "https://api.exchangerate-api.com/v4/latest/USD"
    try:
        req = urllib.request.Request(
            url_secondary,
            headers={"User-Agent": "CryptoSimulatorPeru/2.0"}
        )
        with urllib.request.urlopen(req, timeout=3.0) as response:
            data = json.loads(response.read().decode())
            rate = float(data.get("rates", {}).get("PEN", 0))
            if rate > 2.5:
                return round(rate, 3), True
    except Exception:
        pass

    return DEFAULT_USD_PEN, False


def fetch_mempool_bitcoin_stats() -> Dict[str, Any]:
    """
    Obtiene métricas en vivo de la red Bitcoin desde la API pública de mempool.space:
    - Hashrate global de la red (EH/s)
    - Dificultad actual (en Trillones / T)
    - Altura del último bloque minado
    - Progreso y fecha estimada del próximo ajuste de dificultad
    - Comisiones recomendadas en sat/vB
    """
    default_stats = {
        "hashrate_eh": 720.0,
        "difficulty_t": 110.0,
        "tip_height": 890000,
        "difficulty_change_pct": 1.5,
        "remaining_blocks": 1008,
        "progress_percent": 50.0,
        "fastest_fee_sat": 15,
        "half_hour_fee_sat": 10,
        "is_live": False
    }

    try:
        # 1. Dificultad y progreso del período de 2016 bloques
        req_diff = urllib.request.Request(
            "https://mempool.space/api/v1/difficulty-adjustment",
            headers={"User-Agent": "CryptoSimulatorPeru/2.0"}
        )
        with urllib.request.urlopen(req_diff, timeout=3.5) as r:
            diff_data = json.loads(r.read().decode())
            diff_change = float(diff_data.get("difficultyChange", 1.5))
            rem_blocks = int(diff_data.get("remainingBlocks", 1008))
            prog_pct = float(diff_data.get("progressPercent", 50.0))

        # 2. Hashrate global y dificultad actual
        req_hash = urllib.request.Request(
            "https://mempool.space/api/v1/mining/hashrate/3d",
            headers={"User-Agent": "CryptoSimulatorPeru/2.0"}
        )
        with urllib.request.urlopen(req_hash, timeout=3.5) as r:
            h_data = json.loads(r.read().decode())
            curr_h_raw = float(h_data.get("currentHashrate", 7.2e20))
            curr_h_eh = round(curr_h_raw / 1e18, 2)
            curr_diff_raw = float(h_data.get("currentDifficulty", 1.1e14))
            curr_diff_t = round(curr_diff_raw / 1e12, 2)

        # 3. Altura de bloque
        req_tip = urllib.request.Request(
            "https://mempool.space/api/blocks/tip/height",
            headers={"User-Agent": "CryptoSimulatorPeru/2.0"}
        )
        with urllib.request.urlopen(req_tip, timeout=3.5) as r:
            tip_height = int(r.read().decode().strip())

        # 4. Comisiones recomendadas
        fastest_fee = 10
        try:
            req_fee = urllib.request.Request(
                "https://mempool.space/api/v1/fees/recommended",
                headers={"User-Agent": "CryptoSimulatorPeru/2.0"}
            )
            with urllib.request.urlopen(req_fee, timeout=3.0) as r:
                fee_data = json.loads(r.read().decode())
                fastest_fee = int(fee_data.get("fastestFee", 10))
        except Exception:
            pass

        return {
            "hashrate_eh": curr_h_eh,
            "difficulty_t": curr_diff_t,
            "tip_height": tip_height,
            "difficulty_change_pct": round(diff_change, 2),
            "remaining_blocks": rem_blocks,
            "progress_percent": round(prog_pct, 1),
            "fastest_fee_sat": fastest_fee,
            "is_live": True
        }
    except Exception:
        return default_stats


def fetch_local_miner_status(ip_address: str, timeout: float = 2.5) -> Dict[str, Any]:
    """
    Consulta la API local de un minero Bitaxe o Lucky Miner (AxeOS / ESP32).
    Si ip_address == 'demo', retorna datos simulados realistas.
    """
    clean_ip = ip_address.strip().replace("http://", "").replace("https://", "").rstrip("/")
    if not clean_ip or clean_ip.lower() == "demo":
        return {
            "connected": True,
            "is_demo": True,
            "model": "Lucky Miner LV08 (Demo)",
            "hashrate_gh": 4518.2,
            "temp_c": 56.4,
            "fan_rpm": 3850,
            "voltage_v": 12.1,
            "current_a": 9.8,
            "power_w": 118.6,
            "best_diff": "4.21G (¡Cerca de Bloque!)",
            "uptime_hours": 142.5,
            "pool": "solo.ckpool.org:3333",
            "user": "bc1q9x78df...valle_chicama",
            "firmware": "AxeOS v2.3.1 (ESP32-S3)",
            "msg": "Conectado exitosamente en modo demostración."
        }
    
    url = f"http://{clean_ip}/api/system/info"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CryptoSimulator/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode())
            return {
                "connected": True,
                "is_demo": False,
                "model": str(data.get("ASICModel", "Bitaxe / Lucky Miner")),
                "hashrate_gh": float(data.get("hashRate", data.get("hashrate", 0))),
                "temp_c": float(data.get("temp", data.get("vrTemp", 0))),
                "fan_rpm": int(data.get("fanSpeed", data.get("fanrpm", 0))),
                "voltage_v": float(data.get("voltage", 0)) / (1000.0 if float(data.get("voltage", 0)) > 100 else 1.0),
                "power_w": float(data.get("power", 0)),
                "best_diff": str(data.get("bestDiff", data.get("best_diff", "N/A"))),
                "uptime_hours": round(float(data.get("uptime", 0)) / 3600.0, 1),
                "pool": f"{data.get('stratumURL', 'N/A')}:{data.get('stratumPort', '')}",
                "user": str(data.get("stratumUser", "N/A")),
                "firmware": str(data.get("version", "AxeOS")),
                "msg": f"Conexión exitosa con el minero en {clean_ip}."
            }
    except Exception as e:
        return {
            "connected": False,
            "is_demo": False,
            "msg": f"No se pudo conectar a http://{clean_ip}/api/system/info ({str(e)}). Verifica que tu PC y el minero estén en la misma red WiFi."
        }
