data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  vpc_cidr        = "10.10.0.0/16"
  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  public_subnets  = ["10.10.0.0/20", "10.10.16.0/20", "10.10.32.0/20"]
  private_subnets = ["10.10.128.0/20", "10.10.144.0/20", "10.10.160.0/20"]
}

resource "aws_vpc" "main" {
  cidr_block           = local.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project}-vpc"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project}-igw"
  }
}

resource "aws_subnet" "public" {
  for_each = toset(["0", "1", "2"])

  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.public_subnets[tonumber(each.value)]
  availability_zone       = local.azs[tonumber(each.value)]
  map_public_ip_on_launch = true

  tags = {
    Name                                        = "${var.project}-public-${each.value}"
    "kubernetes.io/role/elb"                    = "1"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }
}

resource "aws_subnet" "private" {
  for_each = toset(["0", "1", "2"])

  vpc_id            = aws_vpc.main.id
  cidr_block        = local.private_subnets[tonumber(each.value)]
  availability_zone = local.azs[tonumber(each.value)]

  tags = {
    Name                                        = "${var.project}-private-${each.value}"
    "kubernetes.io/role/internal-elb"           = "1"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }
}

resource "aws_eip" "nat" {
  for_each = toset(["0", "1", "2"])

  domain = "vpc"

  tags = {
    Name = "${var.project}-nat-eip-${each.value}"
  }
}

resource "aws_nat_gateway" "nat" {
  for_each = toset(["0", "1", "2"])

  allocation_id = aws_eip.nat[each.value].id
  subnet_id     = aws_subnet.public[each.value].id

  tags = {
    Name = "${var.project}-nat-${each.value}"
  }

  depends_on = [
    aws_internet_gateway.igw
  ]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project}-rtb-public"
  }
}

resource "aws_route" "public_inet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public_assoc" {
  for_each = toset(["0", "1", "2"])

  subnet_id      = aws_subnet.public[each.value].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  for_each = toset(["0", "1", "2"])

  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project}-rtb-private-${each.value}"
  }
}

resource "aws_route" "private_nat" {
  for_each = toset(["0", "1", "2"])

  route_table_id         = aws_route_table.private[each.value].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat[each.value].id
}

resource "aws_route_table_association" "private_assoc" {
  for_each = toset(["0", "1", "2"])

  subnet_id      = aws_subnet.private[each.value].id
  route_table_id = aws_route_table.private[each.value].id
}
