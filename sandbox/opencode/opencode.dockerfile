# syntax=docker/dockerfile:1
#
# Companion image recipe for the OpenCode V2 workload kit (opencode.yaml).
#
# Every downloaded artifact is pinned to an exact version and, where the
# upstream publishes one, verified against its official SHA-256 checksum.
# Build-time network access is the builder's; the kit descriptor separately
# declares the runtime egress the agent needs.

FROM ubuntu:24.04

ARG OPENCODE_VERSION=2.0.22
ARG GO_VERSION=1.25.14
ARG GVM_COMMIT=dd652539fa4b771840846f8319fad303c7d0a8d2
ARG NODE_VERSION=24.21.0
ARG UV_VERSION=0.12.23

# Official SHA-256 checksums for the linux/amd64 artifacts:
#   go   https://go.dev/dl/?mode=json
#   node https://nodejs.org/dist/v<ver>/SHASUMS256.txt
#   uv   https://pypi.org/pypi/uv/<ver>/json
ARG GO_SHA256=a21ae5633a269bcd7e90cf767e48225633795e99d831742cbf3397064fee7712
ARG NODE_SHA256=6e1db87ef58b8819e5d5402eff1536491b18edd8eb7bee5ef7897876e88dc5ff
ARG UV_SHA256=565c6e2874dbeae86c02f3dea97255e878fec672659a73d4930c6b93fcab2fff

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
ENV HOME=/home/agent

# System packages: the gvm prerequisites (git, binutils, bison, gcc, make,
# curl), the requested toolchain, archive utilities and Python.
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        bash \
        binutils \
        bison \
        bsdextrautils \
        ca-certificates \
        curl \
        fd-find \
        fzf \
        g++ \
        gcc \
        git \
        gzip \
        jq \
        less \
        libc6-dev \
        make \
        openssh-client \
        pkg-config \
        python3 \
        python3-pip \
        python3-venv \
        ripgrep \
        tar \
        tree \
        unzip \
        wget \
        xz-utils \
        zip; \
    rm -rf /var/lib/apt/lists/*; \
    # Ubuntu ships fd as `fdfind`; expose the conventional command name.
    ln -sf /usr/bin/fdfind /usr/local/bin/fd; \
    command -v fd; command -v rg; command -v fzf

# Non-root agent account (UID/GID 1000) and the writable directories the
# sandbox base requirements expect. Ubuntu 24.04 already ships an `ubuntu`
# account at UID/GID 1000, so normalize that identity to `agent` instead of
# colliding with it.
RUN set -eux; \
    if getent group 1000 >/dev/null; then \
        g="$(getent group 1000 | cut -d: -f1)"; \
        [ "$g" = "agent" ] || groupmod --new-name agent "$g"; \
    else \
        groupadd --gid 1000 agent; \
    fi; \
    if getent passwd 1000 >/dev/null; then \
        u="$(getent passwd 1000 | cut -d: -f1)"; \
        [ "$u" = "agent" ] || usermod --login agent --home /home/agent --move-home --shell /bin/bash "$u"; \
    else \
        useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash agent; \
    fi; \
    usermod -G '' agent; \
    mkdir -p \
        /home/agent/workspace \
        /home/agent/.local/bin \
        /home/agent/.local/share \
        /home/agent/.local/state \
        /home/agent/.cache \
        /home/agent/.config/opencode \
        /home/agent/.docker/sandbox/locks; \
    chown -R agent:agent /home/agent

# Prepare the trust store the proxy-managed sandbox CA is added to at start.
# No certificate is baked into the image.
RUN set -eux; \
    mkdir -p /usr/local/share/ca-certificates /etc/ssl/certs; \
    update-ca-certificates

# Pin toolchain locations so interactive and non-interactive processes agree.
ENV GO_VERSION=${GO_VERSION}
ENV GVM_ROOT=/home/agent/.gvm
ENV GOROOT=/home/agent/.gvm/gos/go${GO_VERSION}
ENV GOPATH=/home/agent/.gvm/pkgsets/go${GO_VERSION}/global
ENV GOTOOLCHAIN=local
ENV PATH=/home/agent/.local/bin:/usr/local/lib/nodejs/bin:${GVM_ROOT}/bin:${GOROOT}/bin:${PATH}

# Proxy CA trust for curl, Node, Python, Go and git. TLS verification is never
# disabled.
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_DIR=/etc/ssl/certs \
    CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    PIP_CERT=/etc/ssl/certs/ca-certificates.crt \
    NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt \
    GIT_SSL_CAINFO=/etc/ssl/certs/ca-certificates.crt

# Node.js LTS from the official tarball, checksum verified.
RUN set -eux; \
    curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.gz" -o /tmp/node.tar.gz; \
    echo "${NODE_SHA256}  /tmp/node.tar.gz" | sha256sum -c -; \
    mkdir -p /usr/local/lib/nodejs; \
    tar -xzf /tmp/node.tar.gz -C /usr/local/lib/nodejs --strip-components=1; \
    rm -f /tmp/node.tar.gz; \
    for bin in node npm npx corepack; do \
        ln -sf "/usr/local/lib/nodejs/bin/${bin}" "/usr/local/bin/${bin}"; \
    done; \
    node --version; npm --version

# uv/uvx from the checksum-verified manylinux x86_64 wheel.
RUN set -eux; \
    uv_wheel="uv-${UV_VERSION}-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"; \
    curl -fsSL "https://files.pythonhosted.org/packages/e5/83/85a6c63c24905af4924fddb11a499b934913f59a134248367a1ef1a4716f/${uv_wheel}" -o "/tmp/${uv_wheel}"; \
    echo "${UV_SHA256}  /tmp/${uv_wheel}" | sha256sum -c -; \
    python3 -m pip install --break-system-packages --no-cache-dir --no-index "/tmp/${uv_wheel}"; \
    rm -f "/tmp/${uv_wheel}"; \
    uv --version; uvx --version

# Go through gvm at a pinned commit. The official Go tarball is downloaded
# here, checksum verified, and seeded into gvm's archive directory so gvm
# installs exactly that verified artifact instead of downloading its own.
USER agent
RUN set -eux; \
    git clone https://github.com/moovweb/gvm.git /tmp/gvm; \
    git -C /tmp/gvm checkout "${GVM_COMMIT}"; \
    bash /tmp/gvm/binscripts/gvm-installer "${GVM_COMMIT}"; \
    rm -rf /tmp/gvm; \
    mkdir -p "${GVM_ROOT}/archive"; \
    curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" -o "${GVM_ROOT}/archive/go${GO_VERSION}.linux-amd64.tar.gz"; \
    echo "${GO_SHA256}  ${GVM_ROOT}/archive/go${GO_VERSION}.linux-amd64.tar.gz" | sha256sum -c -; \
    TERM=xterm bash -c '. "${GVM_ROOT}/scripts/gvm-default"; gvm install "go${GO_VERSION}" -B; gvm use "go${GO_VERSION}" --default; go version; go env GOROOT GOPATH'

# OpenCode V2 from the official npm package, pinned exactly. The package
# provides both the `opencode` and `opencode2` command names.
RUN set -eux; \
    npm install --global --prefix /home/agent/.local --no-fund --no-audit "@opencode/cli@${OPENCODE_VERSION}"; \
    rm -rf /home/agent/.npm; \
    opencode --version; \
    command -v opencode2

# Persistent shell environment: installed once and wired into non-interactive
# (BASH_ENV), interactive (.bashrc) and login (profile.d) shells.
USER root
RUN install -d -m 0755 /usr/local/share/opencode-kit
COPY --chmod=0644 files/shell-env.sh /usr/local/share/opencode-kit/shell-env.sh
RUN set -eux; \
    # Windows-backed build contexts must not leave private parent directories. \
    chmod 0755 /usr/local/share/opencode-kit; \
    chmod 0644 /usr/local/share/opencode-kit/shell-env.sh; \
    touch /etc/sandbox-persistent.sh; \
    chown agent:agent /etc/sandbox-persistent.sh; \
    chmod 0644 /etc/sandbox-persistent.sh; \
    printf '%s\n' '. /etc/sandbox-persistent.sh' > /etc/profile.d/sandbox-persistent.sh; \
    chmod 0644 /etc/profile.d/sandbox-persistent.sh; \
    printf '%s\n' '. /etc/sandbox-persistent.sh' >> /home/agent/.bashrc; \
    printf '%s\n' '. /usr/local/share/opencode-kit/shell-env.sh' >> /etc/sandbox-persistent.sh; \
    chown agent:agent /home/agent/.bashrc
ENV BASH_ENV=/etc/sandbox-persistent.sh

# Launch command. The sbx@1 host reads ENTRYPOINT and runs it as the agent;
# entrypoint.sh performs synchronous setup and execs OpenCode.
COPY --chmod=0755 files/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY --chmod=0755 files/smoke-test.sh /usr/local/bin/smoke-test.sh

USER agent
WORKDIR /home/agent/workspace
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD []
