FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG INSTALL_CODEX_CLI=0

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates curl wget git openssh-client gnupg2 xauth \
    build-essential make cmake pkg-config gcc g++ gdb lldb \
    python3 python-is-python3 python3-pip python3-venv python3-dev \
    netcat-openbsd dnsutils iproute2 iputils-ping traceroute \
    procps psmisc lsof strace tcpdump socat telnet whois file \
    jq ripgrep fd-find fzf shellcheck tree less vim-tiny nano sudo \
    libpq5 libpq-dev \
    tini \
    docker.io docker-buildx docker-compose-v2 gosu \
    libx11-6 libxext6 libxrender1 libxtst6 libxi6 libxrandr2 libxss1 libxkbfile1 \
    libgtk-3-0 libnss3 libnspr4 libasound2t64 libfontconfig1 libfreetype6 \
    libdbus-1-3 xdg-utils fonts-dejavu fonts-liberation \
    libgl1 \
    libglx-mesa0 \
    libgl1-mesa-dri \
    mesa-utils \
 && rm -rf /var/lib/apt/lists/*


RUN if [ "$INSTALL_CODEX_CLI" = "1" ]; then \
      apt-get update \
      && apt-get install -y --no-install-recommends nodejs npm \
      && npm install -g @openai/codex \
      && npm cache clean --force \
      && codex --version ; \
    fi

COPY pycharm/ /opt/pycharm/
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY bootstrap-project.sh /usr/local/bin/docker4ide-bootstrap-project
COPY check-runtime-deps.sh /usr/local/bin/docker4ide-check-runtime-deps
RUN mkdir -p /usr/local/share/docker4ide
COPY image-assets/vibe-coding-process.md /usr/local/share/docker4ide/vibe-coding-process.md
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/docker4ide-bootstrap-project /usr/local/bin/docker4ide-check-runtime-deps /opt/pycharm/bin/pycharm.sh \
 && ln -s /opt/pycharm/bin/pycharm.sh /usr/local/bin/pycharm \
 && printf '%%ide-sudo ALL=(ALL) NOPASSWD:ALL\n' > /etc/sudoers.d/ide-sudo \
 && chmod 0440 /etc/sudoers.d/ide-sudo \
 && mkdir -p /ide-config /var/lib/docker \
 && chmod 0644 /usr/local/share/docker4ide/vibe-coding-process.md

ENV PROJECT_PATH=/workspace/project \
    IDE_GLOBAL_SETTINGS_PATH=/ide-global-settings \
    IDE_PROJECT_STATE_PATH=/ide-project-state \
    HOME=/ide-global-settings/home \
    XDG_CONFIG_HOME=/ide-global-settings/home/.config \
    XDG_CACHE_HOME=/ide-project-state/home/.cache \
    XDG_DATA_HOME=/ide-global-settings/home/.local/share \
    QT_X11_NO_MITSHM=1 \
    _JAVA_AWT_WM_NONREPARENTING=1 \
    LIBGL_ALWAYS_SOFTWARE=1 \
    MESA_LOADER_DRIVER_OVERRIDE=llvmpipe \
    LIBGL_DRI3_DISABLE=1

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
