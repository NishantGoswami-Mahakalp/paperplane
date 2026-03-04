#!/bin/bash
set -e

REGISTRY="${REGISTRY:-}"
TAG="${TAG:-latest}"
PUSH="${PUSH:-false}"

echo "=========================================="
echo "  Building Plane Docker Images"
echo "=========================================="

SERVICES=("api" "web" "admin" "space" "live" "proxy")

build_image() {
    local service=$1
    local dockerfile=$2
    local context=$3
    
    local image_name="${REGISTRY}plane-${service}:${TAG}"
    
    echo "Building ${image_name}..."
    
    docker build \
        --build-arg DOCKER_BUILDKIT=1 \
        -t "${image_name}" \
        -f "${dockerfile}" \
        "${context}"
    
    echo "✓ Built ${image_name}"
    
    if [ "${PUSH}" = "true" ] && [ -n "${REGISTRY}" ]; then
        echo "Pushing ${image_name}..."
        docker push "${image_name}"
    fi
}

# Build all images
build_image "api" "apps/api/Dockerfile.api" "apps/api"
build_image "web" "apps/web/Dockerfile.web" "."
build_image "admin" "apps/admin/Dockerfile.admin" "."
build_image "space" "apps/space/Dockerfile.space" "."
build_image "live" "apps/live/Dockerfile.live" "."
build_image "proxy" "apps/proxy/Dockerfile.ce" "apps/proxy"

echo ""
echo "=========================================="
echo "  Build Complete!"
echo "=========================================="
echo ""
echo "Images built:"
for service in "${SERVICES[@]}"; do
    echo "  - ${REGISTRY}plane-${service}:${TAG}"
done
echo ""
echo "To deploy to VPS:"
echo "  1. Save images: docker save ${REGISTRY}plane-*:${TAG} | gzip > plane-images.tar.gz"
echo "  2. Copy to VPS: scp plane-images.tar.gz user@vps:/tmp/"
echo "  3. On VPS: docker load < /tmp/plane-images.tar.gz"
echo ""
echo "Or push to registry:"
echo "  REGISTRY=myregistry.com PUSH=true TAG=v1.0 ./deploy/build.sh"
