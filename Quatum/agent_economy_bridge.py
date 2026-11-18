import tkinter as tk
import sqlite3
import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name.startswith("layer-") else Path("C:/J-roc-AI/JrocAiDesktopOS")
VAULT_DB = BASE_DIR / "layer-03-memory-vault" / "jroc_os_vault.db"
LEDGER_FILE = BASE_DIR / "layer-10-revenue-sync" / "a2a_economy_ledger.jsonl"

class AgentToAgentEconomyBridge:
    """
    JROC-INV-04: Agent-to-Agent Economy Bridge
    Handles structured JSON task exchange, automated price/comp negotiation,
    and Layer 05 sandbox escrow gating for jrocai.online and resale operations.
    """
    def __init__(self):
        VAULT_DB.parent.mkdir(parents=True, exist_ok=True)
        LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(VAULT_DB))
        self._init_tables()

    def _init_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS a2a_contracts (
                contract_id TEXT PRIMARY KEY,
                counterparty_agent TEXT,
                division TEXT,
                task_type TEXT,
                item_title TEXT,
                offered_price REAL,
                target_price REAL,
                negotiated_price REAL,
                status TEXT,
                payload_json TEXT,
                created_at TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS guardrail_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                swarm_name TEXT,
                action_type TEXT,
                payload TEXT,
                status TEXT DEFAULT 'PENDING_APPROVAL',
                created_at TEXT
            )
        """)
        self.conn.commit()

    def create_structured_a2a_envelope(self, counterparty: str, division: str, task_type: str, item_title: str, target_price: float, min_accept_price: float) -> dict:
        contract_id = f"A2A-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow().isoformat()
        raw_sig = f"{contract_id}:{counterparty}:{target_price}:{timestamp}".encode("utf-8")
        integrity_hash = hashlib.sha256(raw_sig).hexdigest()[:16]

        envelope = {
            "protocol": "JROC-A2A-BRIDGE-v1.0",
            "contract_id": contract_id,
            "sender_node": "JROC-AI-FACTORY-HUB",
            "counterparty_agent": counterparty,
            "division": division,
            "task_type": task_type,
            "asset": {
                "title": item_title,
                "target_price_usd": round(target_price, 2),
                "floor_price_usd": round(min_accept_price, 2),
                "currency": "USD"
            },
            "integrity_hash": integrity_hash,
            "timestamp": timestamp
        }
        return envelope

    def negotiate_comp_exchange(self, counterparty: str, division: str, task_type: str, item_title: str, target_price: float, min_accept_price: float, incoming_offer: float) -> dict:
        envelope = self.create_structured_a2a_envelope(
            counterparty, division, task_type, item_title, target_price, min_accept_price
        )

        # Automated Swarm Negotiation Logic
        if incoming_offer >= target_price:
            agreed_price = round(incoming_offer, 2)
            decision = "ACCEPTED_AT_TARGET"
        elif incoming_offer >= min_accept_price:
            # Counter-split halfway between incoming offer and target price
            agreed_price = round((incoming_offer + target_price) / 2.0, 2)
            decision = "COUNTER_OPTIMIZED"
        else:
            agreed_price = round(min_accept_price, 2)
            decision = "HELD_AT_FLOOR_ESCROW"

        envelope["negotiation_result"] = {
            "incoming_offer_usd": round(incoming_offer, 2),
            "agreed_settlement_usd": agreed_price,
            "decision": decision,
            "guardrail_escrow": "PENDING_HUMAN_APPROVAL"
        }

        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO a2a_contracts (
                contract_id, counterparty_agent, division, task_type,
                item_title, offered_price, target_price, negotiated_price,
                status, payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            envelope["contract_id"], counterparty, division, task_type,
            item_title, incoming_offer, target_price, agreed_price,
            decision, json.dumps(envelope), envelope["timestamp"]
        ))

        # Route settlement through Layer 05 Guardrail Gate
        cur.execute("""
            INSERT INTO guardrail_queue (swarm_name, action_type, payload, status, created_at)
            VALUES (?, ?, ?, 'PENDING_APPROVAL', ?)
        """, (
            f"A2A_BRIDGE_{division}",
            f"SETTLE_{task_type}",
            json.dumps(envelope),
            envelope["timestamp"]
        ))
        self.conn.commit()

        with open(LEDGER_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(envelope) + "\n")

        return envelope

    def list_contracts(self) -> list:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT contract_id, counterparty_agent, division, item_title,
                   offered_price, negotiated_price, status, created_at
            FROM a2a_contracts
            ORDER BY created_at DESC LIMIT 25
        """)
        return cur.fetchall()


class A2AEconomyBridgeHUD(tk.Tk):
    def __init__(self):
        super().__init__()
        self.bridge = AgentToAgentEconomyBridge()
        self.title("JROC-INV-04 // AGENT-TO-AGENT ECONOMY BRIDGE")
        self.geometry("1120x740")
        self.configure(bg="#0a0d12")
        self._build_ui()
        self._refresh_ledger()

    def _build_ui(self):
        header = tk.Frame(self, bg="#11161f", height=48)
        header.pack(fill="x", side="top")
        tk.Label(
            header,
            text="  JROC-INV-04 // AGENT-TO-AGENT ECONOMY BRIDGE  |  PROTOCOL: JROC-A2A-v1.0  |  ESCROW: LAYER-05 GATED",
            fg="#00f0ff", bg="#11161f", font=("Consolas", 10, "bold")
        ).pack(side="left", pady=12)

        body = tk.Frame(self, bg="#0a0d12")
        body.pack(fill="both", expand=True, padx=14, pady=12)

        # Left Panel: A2A Task & Comp Negotiation Builder
        left = tk.Frame(body, bg="#11161f", width=400)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        tk.Label(left, text="DISPATCH A2A NEGOTIATION TASK", fg="#ffffff", bg="#11161f", font=("Consolas", 11, "bold")).pack(pady=(12, 8))

        self.counterparty_var = tk.StringVar(value="External-Market-Comp-Bot-09")
        self.division_var = tk.StringVar(value="COMMERCE")
        self.task_type_var = tk.StringVar(value="COMP_AND_LISTING_EXCHANGE")
        self.item_var = tk.StringVar(value="Vintage Sports Memorabilia Lot #104")
        self.target_var = tk.StringVar(value="180.00")
        self.floor_var = tk.StringVar(value="145.00")
        self.offer_var = tk.StringVar(value="155.00")

        fields = [
            ("Counterparty Agent ID:", self.counterparty_var),
            ("Division Swarm:", self.division_var),
            ("Exchange Task Type:", self.task_type_var),
            ("Asset / Service Title:", self.item_var),
            ("Target Ask Price ($):", self.target_var),
            ("Minimum Floor Price ($):", self.floor_var),
            ("Incoming Agent Offer ($):", self.offer_var)
        ]

        for label_text, var in fields:
            tk.Label(left, text=label_text, fg="#8be9fd", bg="#11161f", anchor="w", font=("Consolas", 9)).pack(fill="x", padx=14, pady=(6, 2))
            tk.Entry(left, textvariable=var, bg="#161d29", fg="#ffffff", insertbackground="#00f0ff", relief="flat", font=("Consolas", 10)).pack(fill="x", padx=14, ipady=5)

        tk.Button(
            left, text="EXECUTE A2A NEGOTIATION & STAGE ESCROW",
            command=self._run_negotiation,
            bg="#00f0ff", fg="#0a0d12", font=("Consolas", 10, "bold"), relief="flat", pady=10
        ).pack(fill="x", padx=14, pady=18)

        # Right Panel: Live JSON Envelope & Contract Ledger
        right = tk.Frame(body, bg="#11161f")
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="STRUCTURED A2A JSON ENVELOPE & SETTLEMENT LEDGER", fg="#00f0ff", bg="#11161f", font=("Consolas", 11, "bold")).pack(pady=(12, 8))

        self.output_box = tk.Text(right, bg="#07090d", fg="#e6edf3", font=("Consolas", 9), relief="flat", padx=12, pady=12)
        self.output_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _run_negotiation(self):
        try:
            target = float(self.target_var.get())
            floor = float(self.floor_var.get())
            offer = float(self.offer_var.get())
        except ValueError:
            self.output_box.insert("end", "[ERROR] Prices must be valid numeric values.\n\n")
            return

        result = self.bridge.negotiate_comp_exchange(
            counterparty=self.counterparty_var.get().strip(),
            division=self.division_var.get().strip(),
            task_type=self.task_type_var.get().strip(),
            item_title=self.item_var.get().strip(),
            target_price=target,
            min_accept_price=floor,
            incoming_offer=offer
        )
        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", "=== LIVE STRUCTURED A2A JSON PAYLOAD (QUEUED IN LAYER 05) ===\n")
        self.output_box.insert("end", json.dumps(result, indent=2) + "\n\n")
        self._refresh_ledger(append=True)

    def _refresh_ledger(self, append=False):
        if not append:
            self.output_box.delete("1.0", "end")
        self.output_box.insert("end", "=== RECENT A2A ECONOMY CONTRACTS (SQLITE VAULT) ===\n")
        contracts = self.bridge.list_contracts()
        if not contracts:
            self.output_box.insert("end", "No A2A contracts executed yet. Dispatch a negotiation task on the left.\n")
        for row in contracts:
            cid, agent, div, title, offer, settled, status, ts = row
            self.output_box.insert("end", f"[{cid}] {div} | {title} | Offer: ${offer:.2f} -> Settled: ${settled:.2f} [{status}]\n")

if __name__ == "__main__":
    app = A2AEconomyBridgeHUD()
    app.mainloop()
