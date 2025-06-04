#!/bin/bash
# Phase 3: Setup Retrieval-Augmented Generation system for Diane
set -e
echo "[Diane Setup] Configuring RAG index folder and reindex script..."
mkdir -p /opt/diane/rag_index
cat <<EOF > /opt/diane/reindex.sh
#!/bin/bash
echo "[Diane] Reindexing RAG files..."
# placeholder for actual reindex command
EOF
chmod +x /opt/diane/reindex.sh
echo "[Diane Setup] RAG configuration complete."
