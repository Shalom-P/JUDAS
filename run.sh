cd llm_server
./run_compose.sh 
cd ../JUDAS
python3 run_manager.py
cd ../llm_server
sudo docker compose down