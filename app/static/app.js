async function placeOrder() {
  const out = document.getElementById("out");
  out.textContent = "queueing order...";
  const order = {
    customer: "Mia",
    delivery_zone: "west",
    items: [
      {id: "milk", qty: 2},
      {id: "eggs", qty: 1},
      {id: "bread", qty: 1}
    ],
    pressure: {
      max_cost: 12,
      risk: 3,
      delay: 2,
      substitution_budget: 3,
      batch_minutes: 9
    }
  };
  const created = await fetch("/api/orders", {
    method: "POST",
    headers: {"content-type": "application/json"},
    body: JSON.stringify(order)
  }).then((res) => res.json());
  for (let i = 0; i < 30; i += 1) {
    const current = await fetch(`/api/orders/${created.order_id}`).then((res) => res.json());
    out.textContent = JSON.stringify(current, null, 2);
    if (current.promise) return;
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
}

document.getElementById("submit").addEventListener("click", () => {
  placeOrder().catch((err) => {
    document.getElementById("out").textContent = err.stack || String(err);
  });
});
