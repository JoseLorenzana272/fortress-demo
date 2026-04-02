# 🏰 Fortress in a Box — Workshop Guide
### 1 Hour | University Students + Junior Engineers

---

## Before the Workshop — Full Environment Setup

### Step 1 — Create a GKE Cluster (15 min)

```bash
# 1. Install Google Cloud CLI if not already installed
# https://cloud.google.com/sdk/docs/install

# 2. Login
gcloud auth login

# 3. Set your project
gcloud config set project YOUR_PROJECT_ID

# 4. Enable the Kubernetes API
gcloud services enable container.googleapis.com

# 5. Create a small cluster (cheap enough for a demo)
gcloud container clusters create fortress-demo \
  --zone us-central1-a \
  --num-nodes 2 \
  --machine-type e2-standard-2 \
  --disk-size 50GB

# 6. Connect kubectl to the new cluster
gcloud container clusters get-credentials fortress-demo \
  --zone us-central1-a

# 7. Verify connection
kubectl get nodes
# Expected: 2 nodes in Ready status
```

> 💡 **Cost:** e2-standard-2 x 2 nodes = ~$0.13/hour.
> Delete the cluster after the workshop:
> `gcloud container clusters delete fortress-demo --zone us-central1-a`

---

### Step 2 — Install the Fortress (5 min)

```bash
# Clone the fortress
git clone https://github.com/JoseLorenzana272/fortress-in-a-box.git
cd fortress-in-a-box

# Run the installer
chmod +x install.sh
./install.sh
```

When prompted:
- **GitHub repo URL:** `https://github.com/JoseLorenzana272/fortress-demo`
- **Discord webhook:** your webhook URL
- **Grafana password:** anything you want (e.g. `fortress-admin`)

Wait ~5 minutes for everything to install.

```bash
# Verify all pods are running
kubectl get pods -n kyverno
kubectl get pods -n falco
kubectl get pods -n monitoring
kubectl get pods -n argocd
```

All pods should show `Running`.

---

### Step 3 — Simulate the NGO App Repo

```bash
# In a new directory — this represents the NGO's own repo
cd ..
git clone https://github.com/JoseLorenzana272/fortress-demo.git
cd fortress-demo

# Deploy both demo apps into the fortress-protected cluster
kubectl apply -f whistleblower-portal/deployment.yaml
kubectl apply -f refugee-tracker/deployment.yaml

# Watch them come up
kubectl get pods -w
```

> **This is the key moment to understand:** The NGO cloned THEIR repo
> and deployed THEIR apps. They never touched fortress-in-a-box after
> running install.sh. The fortress is already protecting everything.

---

### Step 4 — Open Browser Tabs (do this before presenting)

Run each of these in a separate terminal and keep them open:

```bash
# Tab 1 — Grafana (security dashboard)
kubectl port-forward svc/grafana -n monitoring 3000:80
# Open: http://localhost:3000 (admin / your-password)

# Tab 2 — Falcosidekick UI (event browser)
kubectl port-forward svc/falco-falcosidekick-ui -n falco 2802:2802
# Open: http://localhost:2802

# Tab 3 — ArgoCD (GitOps)
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Open: https://localhost:8080

# Tab 4 — Whistleblower Portal
kubectl port-forward svc/whistleblower-portal 8080:80
# Open: http://localhost:8080
```

Also open your Discord `#fortress-alerts` channel on your phone or second screen.

---

### Step 5 — Pre-flight Check

```bash
# All 6 policies should be READY
kubectl get validatingpolicies

# Both demo apps running
kubectl get pods

# Grafana shows SECURE (green)
# open http://localhost:3000

# Make attack script executable
chmod +x attack-simulations.sh
```

✅ You're ready to present.

---

## 00:00 — The Problem (10 min)

> **Speaker notes:** Start with the human story, not the tech.

**Say this:**

*"In 2022, the Red Cross was hacked. Not a small breach — 515,000 people's data stolen. Missing persons. Detainees. People separated from their families by war. The program that helped them find each other had to shut down. Real people couldn't find their missing relatives because of a cyberattack.*

*These organizations have the most sensitive data in the world. And they have zero security budget.*

*Today I'm going to show you what it looks like when they have enterprise-grade security — for free."*

**Show the two demo apps:**
- Open the Whistleblower Portal in browser → walk through the UI
- Show the Refugee Tracker API:
```bash
kubectl run curl-test \
  --image=curlimages/curl \
  --restart=Never \
  --rm -it \
  -- curl http://refugee-tracker/status
```

**Ask the audience:**
*"What happens if a state-sponsored hacker gets into this system? They get whistleblower identities. Refugee locations. They can destroy evidence, silence sources, endanger lives."*

---

## 00:10 — The Installation (10 min)

> **Speaker notes:** Don't do a live install — it takes 5 min and kills momentum.
> Show the terminal output you already have from the prep.

**Say this:**
*"This is the entire installation. One command."*

Show `install.sh` running (or show the completed output):
```
╔════════════════════════════════════════════╗
║         FORTRESS IS ACTIVE ✓               ║
╚════════════════════════════════════════════╝
```

Walk through what each step does:
- **Kyverno installing** → "This is the bouncer. Blocks bad deployments."
- **Falco installing** → "This is the surveillance camera. Watches everything."
- **Grafana installing** → "This is the security monitor. Green means safe."
- **ArgoCD installing** → "This is the self-healing system. Restores anything deleted."

Open Grafana → show the SECURE dashboard.

**Key point:**
*"Five minutes. That's the difference between a vulnerable NGO and a hardened one."*

**Then say this — this is important:**
*"Now — I'm going to show you something. This is a completely separate repository.*
*It's the NGO's own app. They cloned it, deployed it, and the fortress is already protecting it.*
*They never configured anything. They never told the fortress what to watch.*
*It just works."*

Show: `kubectl get pods` — both fortress tools AND demo apps running together.

---

## 00:20 — The Attack Simulations (15 min)

> **Speaker notes:** This is the most important part. Keep energy high.
> Run: `./attack-simulations.sh`

### Attack 1 — Malicious Deployment (2 min)

**Say this:**
*"A hacker gets access to the cluster. First thing they try — deploy their own container."*

```bash
kubectl apply -f bad-actor/deployment.yaml
```

**Expected output:**
```
Error: FORTRESS SECURITY: Running as root is not allowed!
```

**Say this:**
*"Blocked. Before it even ran. The hacker never got a foothold."*

---

### Attack 2 — Root Container (2 min)

**Say this:**
*"They try a simpler approach. Just run a quick container."*

```bash
kubectl run hacker --image=nginx:latest
```

**Expected output:**
```
Error: FORTRESS SECURITY: Using 'latest' image tag is not allowed!
```

**Say this:**
*"Every single deployment must pass 6 security checks. Miss any one — blocked."*

Show the 6 policies:
```bash
kubectl get validatingpolicies
```

---

### Attack 3 — Shell in Container (5 min) ⭐ THE BIG ONE

> **Speaker notes:** Most dramatic demo. Make sure Discord is visible on screen.

**Say this:**
*"The hacker found a vulnerability in the whistleblower portal. They've exploited it.*
*Now they're trying to open a shell — to steal data, move laterally, cover their tracks."*

```bash
# Get the pod name
kubectl get pods

# Open a shell
kubectl exec -it <whistleblower-pod-name> -- /bin/sh
```

**While the shell is open — point to Discord:**
*"Look. The alert fired. Within seconds. The NGO team just got notified on their phones."*

**Point to Grafana:**
*"And here — the dashboard captured the full forensic trail.*
*Who. What. When. Which container. MITRE ATT&CK technique ID. Everything."*

**Say this:**
*"The hacker got in. But they got caught immediately.*
*In the real world, that's the difference between a breach that destroys lives*
*and one that gets contained."*

---

### Attack 4 — Delete Security Policies (5 min)

**Say this:**
*"Smart hackers know about security tools. They try to disable them first."*

```bash
kubectl delete validatingpolicy disallow-root-user
```

**Say this:**
*"Policy deleted. Now they can deploy anything... or can they?"*

**Say while waiting:**
*"ArgoCD is watching the Git repository every 3 minutes.*
*The real state of the cluster lives in Git. Right now Git and the cluster don't match.*
*So ArgoCD is going to fix it."*

```bash
# After ~3 minutes
kubectl get validatingpolicy disallow-root-user
```

**Expected:** Policy is back.

*"Restored. Automatically. Without any human intervention.*
*The hacker's change lasted 3 minutes."*

---

## 00:35 — Deploy Your Own App (15 min)

> **Speaker notes:** Hands-on section. Get the audience involved.

**Say this:**
*"Now you try. Here's what a secure deployment looks like."*

Show `whistleblower-portal/deployment.yaml` — walk through each field:

```yaml
runAsNonRoot: true           # "Can't be root"
privileged: false            # "Can't access the kernel"
readOnlyRootFilesystem: true # "Can't install malware"
resources.limits.cpu         # "Can't exhaust the cluster"
image: app:v1.0.0            # "Must be a pinned version"
```

**Live challenge:**
*"Who can tell me what happens if I remove the resource limits?"*

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: test
spec:
  containers:
    - name: test
      image: nginx:1.25
      securityContext:
        runAsNonRoot: true
        runAsUser: 101
EOF
```

**Expected:** Blocked by `require-resource-limits`.

---

## 00:50 — Q&A + Wrap Up (10 min)

**Key points to reinforce:**

1. **This is free.** Every tool here is open source.
2. **This is real.** The same tools used by enterprises.
3. **This is automated.** No security team required to operate it.
4. **This is GitOps.** Git is the source of truth. Everything is auditable.

**Common questions:**

*Q: What if we use AWS/Azure instead of GKE?*
A: Works on any Kubernetes cluster. Cloud provider doesn't matter.

*Q: What about databases?*
A: Any pod in the cluster is automatically protected. Zero extra config.

*Q: How do we get alerts if we don't use Discord?*
A: Falcosidekick supports 50+ outputs — Slack, email, PagerDuty, webhooks, etc.

*Q: Is this production ready?*
A: The tools are production-grade (used by Google, Shopify, etc.). This is the starting point — a real deployment would add network policies, secrets management, and ingress hardening.

**Close with:**
*"The repo is open source. Star it, fork it, share it with any NGO you know.*
*The goal is to get this into the hands of people who actually need it."*

```
github.com/JoseLorenzana272/fortress-in-a-box
```

---

## Troubleshooting

**Pods not running on GKE:**
```bash
kubectl describe pod <pod-name>
kubectl get events --sort-by='.lastTimestamp'
# GKE sometimes needs a minute for nodes to be fully ready
```

**Kyverno blocking system pods:**
```bash
# Check which namespace is being blocked
kubectl get events -A | grep -i denied
# Add the namespace to policy exclusions if needed
```

**Falco not detecting on GKE:**
```bash
kubectl logs -n falco -l app.kubernetes.io/name=falco | tail -20
# GKE uses modern_ebpf by default - should work fine
```

**ArgoCD not syncing:**
```bash
kubectl get applications -n argocd
# Hard refresh in ArgoCD UI if needed
```

**Port forwarding dropped:**
```bash
# Just re-run the port-forward command
kubectl port-forward svc/grafana -n monitoring 3000:80
```

**After the workshop — DELETE THE CLUSTER:**
```bash
gcloud container clusters delete fortress-demo --zone us-central1-a
```
> This stops all billing immediately.
