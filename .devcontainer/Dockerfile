# ---- build-time knobs -------------------------------------------------
ARG ALPINE_VERSION=3.22


FROM alpine:${ALPINE_VERSION}

# ---- re-declare args so they are visible below FROM -------------------
ARG USERNAME=pn
ARG USER_UID=1000
ARG USER_GID=1000
ARG PYTHON_VERSION=3.12
ARG NODE_MAJOR=22
ARG CLAUDE_CODE_VERSION=latest

ENV PNPM_HOME="/usr/local/share/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
ENV SHELL=/bin/sh
ENV PIPX_BIN_DIR="/home/${USERNAME}/.local/bin" \
    PIPX_HOME="/home/${USERNAME}/.local/share/pipx"
# ---- Python + Node + everyday dev tools in one shot -------------------
RUN apk add --no-cache \
    # python
    python3~=${PYTHON_VERSION} py3-pip \
    # node
    nodejs~=${NODE_MAJOR} npm \
    # usual dev helpers
    bash zsh git curl vim nano jq procps \
    gcc musl-dev libffi-dev openssl-dev make \
    tar xz unzip gnupg sudo \
    pipx && \
    addgroup -g ${USER_GID} ${USERNAME} && \
    adduser -D -u ${USER_UID} -G ${USERNAME} -s /bin/zsh ${USERNAME} && \
    install -d -o ${USERNAME} -g ${USERNAME} \
    "${PIPX_HOME}" "${PIPX_BIN_DIR}" \
     /home/${USERNAME}/.local/share/man && \
    # corepack isn't in alpine. and we don't need it. just install pnpm directly
    npm install -g pnpm@latest && \
    pnpm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}

# ---- firewall helper (kept from your original) ------------------------
COPY init-firewall.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/init-firewall.sh && \
    echo "${USERNAME} ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" \
         > /etc/sudoers.d/${USERNAME}-firewall && \
    chmod 0440 /etc/sudoers.d/${USERNAME}-firewall

# ---- tidy up & switch user -------------------------------------------
RUN rm -rf /tmp/* /var/tmp/* /root/.cache

USER ${USERNAME}
# install tools *as* the user
RUN pipx install poetry==2.1.4 && \
    pipx install pipenv && \
    pipx install uv && \
    pipx install python-dotenv

WORKDIR /home/${USERNAME}