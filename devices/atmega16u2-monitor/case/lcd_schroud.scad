include <../../../../../openscad/libs/BOSL2/std.scad>

$fn=100;

roundingRadius = 2;
wallThickness = 1.6;

generalPadding = 2;
boardHeight = 35;
boardWidth = 64.5;
boardDepth = 16.9;

boardPaddingLeft = 2.4 + 2.2;
boardMarginLeft = 10;
screenCenterX = boardPaddingLeft + boardMarginLeft - 2 + 56.5/2;

screenWidth = 45.8;
screenHeight = 34;

usbAWidth = 12.2;
usbADepth = 5.4;
usbADepthMargin = 3;

m25Hole = 2.5;

caseWidth = boardWidth + 2*generalPadding;
caseHeight = boardHeight + 2*generalPadding;
caseDepth = boardDepth;

screenPadding = 0.8;


// translate([boardWidth/2 + wallThickness + boardPaddingLeft, 0,0])
// #cube([boardWidth, boardHeight,boardDepth], anchor=CENTER+BOTTOM);

difference(){
    // main box
    translate([0,-(caseHeight+2*wallThickness)/2,0])
        difference(){
            cuboid([caseWidth+2*wallThickness,caseHeight+2*wallThickness,caseDepth+wallThickness], rounding=roundingRadius, anchor=BOTTOM+FRONT+LEFT);
            translate([wallThickness, wallThickness, -1])
                cube([caseWidth,caseHeight,caseDepth+1]);
        }

    // usb cutout
    cube([usbAWidth,usbAWidth,usbADepth+usbADepthMargin], anchor=CENTER+BOTTOM);

    // screen cutout
    translate([screenCenterX,0,0]) {
        cube([screenWidth+screenPadding, screenHeight+screenPadding, caseDepth + 10], anchor=CENTER+BOTTOM);
        xOffset = 56.5/2-2.5;
        yOffset = 34/2-2;
        for(x=[-xOffset, +xOffset]) for(y=[-yOffset, yOffset]) translate([x,y,0])
        cylinder(d=m25Hole, h=caseDepth+10);
    }
}
