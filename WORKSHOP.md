# 🏰 Fortress in a Box — Demo Runbook

---

## 1) Pre-condition: demo apps already running

The idea is to show that the organization already has its own application repository and deploys its app normally. Fortress is installed afterward and protects the cluster without requiring app changes.

```bash
# from the repo that contains the NGO demo apps
cd fortress-demo

# deploy the apps
kubectl apply -f whistleblower-portal/deployment.yaml
kubectl apply -f refugee-tracker/deployment.yaml

# verify they are up
kubectl get pods
kubectl get svc
```

Expected result:
- both demo apps are running
- the apps are in the cluster before Fortress is installed

Optional:

```bash
# open the app in a browser
kubectl port-forward svc/whistleblower-portal 8081:80
# open http://localhost:8081
```

---

## 2) Clone Fortress and install it

```bash
cd ..
git clone https://github.com/JoseLorenzana272/fortress-in-a-box.git
cd fortress-in-a-box
chmod +x install.sh
./install.sh
```

When prompted, use values such as:
- GitHub repo URL: `https://github.com/JoseLorenzana272/fortress-demo`
- Discord webhook: your webhook URL
- Grafana password: any value you want (example: `fortress-admin`)

Wait for the installation to finish.

```bash
# verify the security stack is running
kubectl get pods -n kyverno
kubectl get pods -n falco
kubectl get pods -n monitoring
kubectl get pods -n argocd
```

Expected result:
- all main Fortress components are in `Running` state
- the demo apps remain running
- the cluster now has Kyverno, Falco, Grafana, and ArgoCD installed

---

## 3) Prepare dashboards and browser tabs

Run the following in separate terminals before the tests:

```bash
# Grafana
kubectl port-forward svc/grafana -n monitoring 3000:80
# open http://localhost:3000

# Falcosidekick UI
kubectl port-forward svc/falco-falcosidekick-ui -n falco 2802:2802
# open http://localhost:2802

# ArgoCD
kubectl port-forward svc/argocd-server -n argocd 8080:443
# open https://localhost:8080

# Whistleblower Portal
kubectl port-forward svc/whistleblower-portal 8081:80
# open http://localhost:8081
```

Optional: open your Discord `#fortress-alerts` channel on your phone or second screen.

---

## 4) Validate the stack before testing

```bash
# all security policies should exist
kubectl get validatingpolicies

# verify the environment is ready
kubectl get pods
kubectl get ns
```

You should see the project apps and the Fortress namespaces working together.

---

## 5) Run the security tests

### Test 1 — malicious deployment is blocked by Kyverno

```bash
kubectl apply -f bad-actor/deployment.yaml
```

Expected result:
- the deployment is denied
- Kyverno blocks it before the container runs

---

### Test 2 — root container is blocked

```bash
kubectl run hacker --image=nginx:latest
```

Expected result:
- the command is denied
- Kyverno blocks the latest tag and root user policies

---

### Test 3 — shell in running container triggers Falco

Get the pod name first:

```bash
kubectl get pods
```

Then try to open a shell in the app pod:

```bash
kubectl exec -it <whistleblower-pod-name> -- /bin/sh
```

Expected result:
- Falco fires an alert
- Discord receives the notification
- Grafana shows the event in the security logs

---

### Test 4 — delete a policy and verify ArgoCD restores it

```bash
kubectl delete validatingpolicy disallow-root-user
```

Then wait for ArgoCD to reconcile:

```bash
kubectl get validatingpolicy disallow-root-user
```

Expected result:
- the policy reappears automatically
- ArgoCD restores the desired state from Git

---

## 6) Optional: run the bundled demo script

If you want the reusable script instead of individual commands:

```bash
chmod +x attack-simulations.sh
./attack-simulations.sh
```

This script runs the same attack flow in sequence.

---

## 7) Useful checks during the demo

```bash
# check Kyverno policies
kubectl get validatingpolicies

# check Falco-related pods
kubectl get pods -n falco

# check monitoring stack
kubectl get pods -n monitoring

# check ArgoCD apps
kubectl get applications -n argocd
```

---

## 8) Troubleshooting

### Pods not ready

```bash
kubectl describe pod <pod-name>
kubectl get events --sort-by='.lastTimestamp'
```

### Falco no alert is visible

```bash
kubectl logs -n falco -l app.kubernetes.io/name=falco --tail=40
```

### ArgoCD is not restoring

```bash
kubectl get applications -n argocd
```

### Port-forward issue

```bash
kubectl port-forward svc/grafana -n monitoring 3000:80
kubectl port-forward svc/falco-falcosidekick-ui -n falco 2802:2802
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

---
