module.exports = {
  apps: [{
    name: 'spirit-bead-backend',
    script: '/var/www/spirit-bead-backend/venv/bin/python',
    args: 'manage.py runserver 0.0.0.0:8000',
    cwd: '/var/www/spirit-bead-backend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      DJANGO_SETTINGS_MODULE: 'spiritbead.settings'
    },
    log_file: '/var/www/spirit-bead-backend/logs/combined.log',
    out_file: '/var/www/spirit-bead-backend/logs/out.log',
    error_file: '/var/www/spirit-bead-backend/logs/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true
  }]
};
