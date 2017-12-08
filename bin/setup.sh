
# install systemd config to run beam as a service (BAAS)
sudo cp /home/pi/workspace/beam/bin/beam.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/beam.service
sudo chmod +x /home/pi/workspace/beam/beam.py
sudo systemctl daemon-reload
sudo systemctl enable beam
sudo systemctl start beam

cp bin/postmerge.sh .git/hooks/post-merge

# Other interesting commands:
# sudo systemctl status beam
# sudo systemctl start beam
# sudo systemctl stop beam
# sudo journalctl -f -u beam

