ARG PYTHON_VERSION=3.12
ARG LINUX_VERSION=alpine3.22
ARG NODE_VERSION=24.11.0
ARG CLAUDE_CODE_VERSION=latest

FROM python:${PYTHON_VERSION}-${LINUX_VERSION}

# Set shell and environment
SHELL ["/bin/sh", "-euo", "pipefail", "-c"]
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off


# Install system dependencies for Python
RUN apk add --no-cache \
    bash \
    zsh \
    curl \
    gnupg \
    tar \
    xz \
    git \
    gcc \
    delta \
    fzf \
    unzip \
    gh \
    iptables \
    ipset \
    iproute2 \
    dnsutils \
    aggregate \
    jq \
    nano \
    vim \
    procps \
    musl-dev \
    libffi-dev \
    openssl-dev \
    pipx \
    make \
    && pipx install poetry==2.1.4

# Create a non-root user
RUN addgroup -g 1000 pn && \
    adduser -D -u 1000 -G pn -s /bin/zsh pn

# Install Node.js 24 from official binary (Alpine-compatible)
RUN ARCH="x64" && \
    curl -fsSLO --compressed "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${ARCH}-musl.tar.xz" && \
    curl -fsSLO --compressed "https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt.asc" && \
    gpg --keyserver hkps://keys.openpgp.org --recv-keys 94AE36675C464D64BAFA68DD7434390BDBE9B9C5 && \
    gpg --batch --decrypt --output SHASUMS256.txt SHASUMS256.txt.asc && \
    grep " node-v${NODE_VERSION}-linux-${ARCH}-musl.tar.xz\$" SHASUMS256.txt | sha256sum -c - && \
    tar -xJf "node-v${NODE_VERSION}-linux-${ARCH}-musl.tar.xz" -C /usr/local --strip-components=1 --no-same-owner && \
    rm "node-v${NODE_VERSION}-linux-${ARCH}-musl.tar.xz" SHASUMS256.txt.asc SHASUMS256.txt && \
    ln -s /usr/local/bin/node /usr/local/bin/nodejs

# Enable pnpm via Corepack
RUN corepack enable && \
    corepack prepare pnpm@latest --activate

# Install Python tools (Poetry, pipenv, uv)
RUN pip install pipenv uv python-dotenv && \
    rm -rf /root/.cache/pip

# Install Claude
RUN pnpm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}


# Copy and set up firewall script
COPY init-firewall.sh /usr/local/bin/
USER root
RUN chmod +x /usr/local/bin/init-firewall.sh && \
  echo "pn ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" > /etc/sudoers.d/pn-firewall && \
  chmod 0440 /etc/sudoers.d/pn-firewall && \
  rm -rf /tmp/* /var/tmp/* /usr/local/lib/node_modules/npm/cache


# Switch to non-root user
USER pn
WORKDIR /home/pn
