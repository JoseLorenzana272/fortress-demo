#!/bin/bash

# ============================================================
# FORTRESS IN A BOX — Attack Simulation Script
# Workshop Demo — Run these attacks live to show the audience
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

pause() {
  echo -e "\n${YELLOW}Press ENTER to continue...${NC}"
  read -r
}

header() {
  clear
  echo -e "${BLUE}"
  echo "╔════════════════════════════════════════════════════════╗"
  echo "║           FORTRESS IN A BOX — LIVE ATTACK DEMO        ║"
  echo "╚════════════════════════════════════════════════════════╝"
  echo -e "${NC}"
}

# ============================================================
# ATTACK 1 — Try to deploy a malicious insecure container
# ============================================================
attack_1() {
  header
  echo -e "${RED}⚔  ATTACK 1: Deploying a malicious container${NC}"
  echo -e "${CYAN}Scenario: A hacker gains access to the cluster and tries"
  echo -e "to deploy a privileged container running as root.${NC}\n"
  echo -e "Running: kubectl apply -f bad-actor/deployment.yaml\n"
  pause

  kubectl apply -f bad-actor/deployment.yaml 2>&1 || true

  echo -e "\n${GREEN}✓ FORTRESS BLOCKED IT${NC}"
  echo -e "Kyverno denied the deployment before it ever ran."
  pause
}

# ============================================================
# ATTACK 2 — Try to run a root container directly
# ============================================================
attack_2() {
  header
  echo -e "${RED}⚔  ATTACK 2: Spawning a root container${NC}"
  echo -e "${CYAN}Scenario: Attacker tries to run a quick root container"
  echo -e "to gain access to the node filesystem.${NC}\n"
  echo -e "Running: kubectl run hacker --image=nginx:latest\n"
  pause

  kubectl run hacker --image=nginx:latest 2>&1 || true

  echo -e "\n${GREEN}✓ FORTRESS BLOCKED IT${NC}"
  echo -e "Two policies triggered: disallow-latest-tag + disallow-root-user"
  pause
}

# ============================================================
# ATTACK 3 — Shell inside a running container (Falco demo)
# ============================================================
attack_3() {
  header
  echo -e "${RED}⚔  ATTACK 3: Opening a shell inside a running container${NC}"
  echo -e "${CYAN}Scenario: A hacker has exploited a vulnerability in the"
  echo -e "whistleblower portal and opens a reverse shell.${NC}\n"
  echo -e "${YELLOW}Watch your Discord channel and Grafana dashboard!${NC}\n"

  POD=$(kubectl get pod -l app=whistleblower-portal -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

  if [ -z "$POD" ]; then
    echo -e "${RED}Whistleblower portal not running. Deploy it first:${NC}"
    echo -e "kubectl apply -f whistleblower-portal/deployment.yaml"
    pause
    return
  fi

  echo -e "Target pod: ${POD}"
  echo -e "Running: kubectl exec -it ${POD} -- /bin/sh\n"
  pause

  kubectl exec -it "$POD" -- /bin/sh || true

  echo -e "\n${GREEN}✓ FALCO DETECTED IT${NC}"
  echo -e "Check Discord — alert should have fired within seconds."
  echo -e "Check Grafana — Security Events Log shows the intrusion."
  pause
}

# ============================================================
# ATTACK 4 — Try to delete security policies (ArgoCD demo)
# ============================================================
attack_4() {
  header
  echo -e "${RED}⚔  ATTACK 4: Deleting security policies${NC}"
  echo -e "${CYAN}Scenario: An attacker with cluster access tries to disable"
  echo -e "the security policies so they can deploy anything they want.${NC}\n"
  echo -e "Running: kubectl delete validatingpolicy disallow-root-user\n"
  pause

  kubectl delete validatingpolicy disallow-root-user 2>&1 || true

  echo -e "\n${YELLOW}Policy deleted. Waiting 3 minutes for ArgoCD to restore it...${NC}"
  echo -e "Watch the ArgoCD dashboard — it will detect the drift.\n"

  echo -e "Checking every 30 seconds..."
  for i in 1 2 3 4 5 6; do
    sleep 30
    STATUS=$(kubectl get validatingpolicy disallow-root-user 2>/dev/null | grep -c "disallow-root-user" || echo "0")
    if [ "$STATUS" -gt "0" ]; then
      echo -e "\n${GREEN}✓ ARGOCD RESTORED IT${NC}"
      echo -e "ArgoCD detected the drift and restored the policy from Git."
      echo -e "The attacker's change was automatically undone."
      break
    else
      echo -e "  [${i}/6] Still waiting... (${i}m elapsed)"
    fi
  done
  pause
}

# ============================================================
# MAIN MENU
# ============================================================
main() {
  header
  echo -e "Choose an attack simulation:\n"
  echo -e "  ${RED}1${NC} — Deploy malicious container (Kyverno blocks)"
  echo -e "  ${RED}2${NC} — Spawn root container (Kyverno blocks)"
  echo -e "  ${RED}3${NC} — Shell in container (Falco detects + Discord alert)"
  echo -e "  ${RED}4${NC} — Delete security policies (ArgoCD restores)"
  echo -e "  ${RED}a${NC} — Run ALL attacks in sequence"
  echo -e "  ${RED}q${NC} — Quit\n"

  read -r -p "Select: " choice

  case $choice in
    1) attack_1 ;;
    2) attack_2 ;;
    3) attack_3 ;;
    4) attack_4 ;;
    a) attack_1; attack_2; attack_3; attack_4 ;;
    q) exit 0 ;;
    *) echo "Invalid choice" ;;
  esac

  main
}

main
