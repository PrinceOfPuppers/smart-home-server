use <./resources/cloister.ttf>
use <../../../../openscad/libs/BOSL2/std.scad>

$fn=50;

m3Hole = 3.3;

m3Hex = 5.95 + 0.35;
m3HexDepth=2.4;

motorShaftDiameter = 6;
motorKeyDiameter = 5.4;

screwBore = 2.4;
chainGearDepth = 10;

pressFit = 0;
tightFit = 0.127;
normalFit = 0.254;
looseFit = 0.508;

standardWasherDepth = 1;

chainGearRimDiameter = 2*23;

// has to be close to chain gear rim diameter, used for other calculations (ie positioning of chain guides)
// its a seperate variable so they can be edited independantly
chainGearRimDiameterEffective = 2*20;

chainGearScaling = 0.95;

largeBeadDiameter = 1.1*9.7;


module rectTube(w, h, l, t){
    difference(){
        cube([w,h,l]);
        translate([t/2,-1,t/2]) cube([w-t,h+2,l-t]);
    }
}

module collar(diameter, thickness, height, setScrew){
    difference(){
        cylinder(d=diameter+thickness, h=height);
        translate([0,0,-1])
            cylinder(d=diameter, h=height+2);

        translate([0,0,height/2]) rotate([0, 90, 0])
            cylinder(d=setScrew, h=(thickness+diameter)/2 + 1);
    }

}


chainGearRim = 5;


function chainGearDiameter(teeth, pitch, additionalRadius) = (1000*teeth/pitch)/3.141592653 + 2*additionalRadius;
function chainGearHeight(beadDiameter, rim, oversizing) = oversizing*beadDiameter + 2*rim;


module chainGearNew(teeth, pitch, beadDiameter, height, additionalRadius){
    oversizing = 1.2;
    linkageDiameter = 1.0;
    //additionalRadius = 1;
    additionalRadiusFlange = 0.3;
    oversizedDiameter = beadDiameter*oversizing;
    oversiedLinkage = linkageDiameter*oversizing;

    outerDiameter = chainGearDiameter(teeth,pitch, additionalRadius);
    diameter = outerDiameter-2*additionalRadius;

    difference(){

        translate([0,0,-height/2])
        cylinder(d=outerDiameter, h=height);

        dtheta = 360/teeth;

        for(i = [0:dtheta:360]){
            translate([diameter*cos(i)/2, diameter*sin(i)/2, 0]){
                sphere(d=oversizedDiameter);
                rotate([0,90,i]) translate([0,0,0])
                    cylinder(d1=oversizedDiameter, d2=oversizedDiameter+additionalRadiusFlange, h=additionalRadius+0.01);
            }
        }
        for(i=[dtheta/2:dtheta:360+dtheta/2]){
            translate([diameter*cos(i)/2, diameter*sin(i)/2, 0]){
                rotate([90,0,i]) {
                    translate([0,0,-2])
                        cylinder(d=linkageDiameter, h=4);
                    rotate([0,90,0])
                        prismoid(size1=[4,linkageDiameter], size2=[4,linkageDiameter+additionalRadiusFlange], height=additionalRadius+0.01);
                }
            }
        }
    }
}

module chainGear(bore, keyDiameter, fit){
    baseHeight = 6;
    beadDiameter = 4.5;
    teeth = 20;
    pitch = 161;
    baseDiameter = chainGearDiameter(teeth, pitch, 1);
    chainGearSlopeHeight = (chainGearDepth-baseHeight)/2;

    difference(){
        scale([chainGearScaling, chainGearScaling, 1])
        union(){
            translate([0,0, chainGearDepth/2]) chainGearNew(teeth, pitch, beadDiameter, baseHeight, 1);

            // upper and lower ramp
            difference(){
                union(){
                    translate([0,0, chainGearDepth-chainGearSlopeHeight])
                        cylinder(d1=baseDiameter, d2=chainGearRimDiameter, h=chainGearSlopeHeight);

                    translate([0,0,chainGearSlopeHeight]) rotate([180,0,0])
                        cylinder(d1=baseDiameter, d2=chainGearRimDiameter, h=chainGearSlopeHeight);
                }
            }
        }
        // bore
        
        boreDiam = bore + fit;

        difference(){
        translate([0,0,-chainGearDepth/2]){
                cylinder(d=boreDiam, h=2*chainGearDepth);
            }
            translate([-boreDiam/2,-boreDiam/2+(keyDiameter+fit),-chainGearDepth/2])
                cube([boreDiam,boreDiam,2*chainGearDepth]);
        }

    }
}

module chainGear_v2(){
    shaftHolderDiameter = 10;
    screwPosDiameter = 16;

    // for loop for slicing in 2
    for(s=[0,180]) translate([-s/50,0,0]) {
        intersection(){
            // mask
            rotate([0,0,s]) translate([0.1,-(chainGearRimDiameter/2+1),-1])
                cube([chainGearRimDiameter+2,chainGearRimDiameter+2,chainGearDepth+2]);

            // full gear
            difference(){
                rotate([0,0,45])
                chainGear(motorShaftDiameter, motorKeyDiameter, tightFit);

                // cutouts
                translate([0,0,-1]){
                    cylinder(d=shaftHolderDiameter+0.9, h=chainGearDepth+2);
                    for(i=[0:90:3*90]){
                        rotate([0,0,i+45]) translate([screwPosDiameter/2,0,0]) cylinder(d=m3Hole, chainGearDepth+2);
                        rotate([0,0,i]) translate([shaftHolderDiameter/2-2,0,0]) cylinder(d=6.7, chainGearDepth+2);
                        rotate([0,0,i+45]) translate([screwPosDiameter/2,0,0]) rotate([0,0,30]) cylinder($fn = 6, h = m3HexDepth+1, d = m3Hex);
                    }
                }
            }
        }
    }

}

module washer(inner, thickness, depth){
    outer = inner + thickness;
    difference(){
        cylinder(d=outer, h = depth);
        translate([0,0,-1])
            cylinder(d=inner, h = depth+2);
    }
}

module copy_mirror(vec){
    children();
    mirror(vec)
    children();
}

poleDiameter = 5;
poleHeight = 21;

module motorHousing(){
    // housing wall thickness
    t = 4.7;

    //cylinder radius (some scaled multiple of chain gear radius)
    cr = 1.2*chainGearScaling*chainGearRimDiameterEffective/2;

    // cube above the cylinder
    cubeLength = 1.3*cr;

    // wm stands for wallmount
    wmDepth = 19;
    wmWidth= 40;
    wmHeight = 90;

    
    // 1 for yes 0 for no
    applyMirror = 1;

    mirror([0,0,applyMirror]) difference(){
        union(){
            rotate([0,90,0]) cylinder(r=cr, h=t);
            translate([0,-cubeLength,-cr]) cube([t,cubeLength,2*cr]);

            copy_mirror([0,0,1]){
                translate([0,-cubeLength+poleDiameter/2,cr-poleDiameter/2]) rotate([0, -90, 0]) cylinder(d=poleDiameter, h=poleHeight);
            }

            // cut out to make swoops
            translate([0,-wmHeight/2,0]) cube([t,wmHeight,cr]);

            // wall mount
            translate([0, wmHeight/2, cr-t]) rotate([0,0,-90]){
                cube([wmHeight,wmWidth+t,t]);
                cube([wmHeight,t,wmDepth+t]);
            }

        }

        // motor holes
        translate([t+1,0,0]) rotate([180,90,0]) motorHoles();

        // swoop cutout
        swoopScaling = (cr-t)/(wmHeight/2-cr);
        scale([1,1,swoopScaling]) translate([-1,wmHeight/2,0]) rotate([0,90,0]) cylinder(r=wmHeight/2-cr, h=t+2);
        swoopScaling2 = (cr-t)/(wmHeight/2-cubeLength);
        scale([1,1,swoopScaling2]) translate([-1,-wmHeight/2,0]) rotate([0,90,0]) cylinder(r=wmHeight/2-cubeLength, h=t+2);


        translate([0,0,cr+wmDepth/2]) difference(){
            minkowski() {
              cube([2,wmHeight-2*t-1,wmDepth-1.5*t-1],center=true);
              rotate([0,90,0]) cylinder(r=1,h=1);
            }
            rotate([90,0,-90]) translate([0,0,-10]) linear_extrude(20) mirror([0,applyMirror,0]) text(size=7.9, "Der Jalousienheber", font="Cloister Black:style=Light", halign="center", valign="center");

        }

        // corner cuts for print bed adheasion
        translate([0, -wmHeight,-cr-t/4]) rotate([0,45,0]) cube([10, 2*wmHeight, wmHeight]);
    }
}


module chainGuide(){
    tourisRadius = chainGearRimDiameterEffective/2;
    thickness = 3;

    poleOffset = -tourisRadius+poleDiameter/2+thickness/2;

    translate([-poleOffset,0,0])
    difference(){
        union(){
            // guide
                wallHeight = thickness + largeBeadDiameter - sqrt(largeBeadDiameter*largeBeadDiameter - chainGearDepth*chainGearDepth/4);
                difference(){
                rotate_extrude() translate([-poleOffset+wallHeight+thickness, 0, 0]) rotate([0,0,180]) difference(){
                    translate([0,-chainGearDepth/2])
                    square([chainGearDepth/2+thickness,chainGearDepth]);
                    translate([0,0,0]) circle(d = largeBeadDiameter);
                }

                // cut in half
                translate([-2*tourisRadius,0,-2*chainGearDepth]) cube([4*tourisRadius,2*tourisRadius,4*chainGearDepth]);
            }

            // cyllinder
            translate([poleOffset,0,-chainGearDepth/2]) cylinder(d=poleDiameter+2*thickness, h = chainGearDepth);
        }

        // cutout shaft
        translate([poleOffset,0, - chainGearDepth])
            cylinder(d=poleDiameter+normalFit, h = chainGearDepth*2);
    }

}

module fullAssembly(){
    motorHousing();
    translate([0,0,0]) rotate([0,-90,0]) 
        washer(motorShaftDiameter+1.2*looseFit,4.5,standardWasherDepth);
    translate([-standardWasherDepth,0,0]) rotate([0,-90,0]) 
        washer(motorShaftDiameter+1.2*looseFit,4.5,standardWasherDepth);
    translate([-2*standardWasherDepth,0,0]) rotate([0,-90,0]) 
        washer(motorShaftDiameter+1.2*looseFit,4.5,standardWasherDepth);
    translate([-3*standardWasherDepth,0,0]) rotate([0,-90,0]) 
        chainGear(motorShaftDiameter, motorKeyDiameter, tightFit);

    cr = 1.2*chainGearScaling*chainGearRimDiameterEffective/2;
    cubeLength = 1.3*cr;

    copy_mirror([0,0,1]){
        translate([-chainGearDepth/2-3*standardWasherDepth,-cubeLength+poleDiameter/2,cr-poleDiameter/2]) {
            rotate([90,-20,-90]){
                chainGuide();
            }
            translate([-chainGearDepth/2 - 1*standardWasherDepth,0,0]) rotate([0,-90,0])
                collar(poleDiameter+looseFit, 6, 5, screwBore);
            translate([-chainGearDepth/2 ,0,0]) rotate([0,-90,0])
                washer(poleDiameter+looseFit,3,standardWasherDepth);
            translate([+chainGearDepth/2+2*standardWasherDepth,0,0]) {
                rotate([0,-90,0])
                    washer(poleDiameter+looseFit,3,standardWasherDepth);
                translate([-1,0,0]) rotate([0,-90,0])
                    washer(poleDiameter+looseFit,3,standardWasherDepth);
            }
            translate([+chainGearDepth/2+3*standardWasherDepth,0,0]) {
                rotate([0,-90,0])
                    washer(poleDiameter+looseFit,3,standardWasherDepth);
                translate([-1,0,0]) rotate([0,-90,0])
                    washer(poleDiameter+looseFit,3,standardWasherDepth);
            }
        }
    }
}

module printReady(){
    translate([-25,0,0]) rotate([0,45,0])
    motorHousing();
    translate([30,0,0])
    washer(motorShaftDiameter+1.2*looseFit,4.5,standardWasherDepth);
    translate([30,15,0])
    washer(motorShaftDiameter+1.2*looseFit,4.5,standardWasherDepth);
    translate([30,30,0])
    washer(motorShaftDiameter+1.2*looseFit,4.5,standardWasherDepth);
    translate([60,0,0])
    chainGear(motorShaftDiameter, motorKeyDiameter, tightFit);

    translate([60,50,chainGearDepth]) rotate([180,0,0])
    chainGear_v2();


    translate([100,0,0])
    chainGuide();
    translate([100,30,0])
    chainGuide();
    translate([150,0,0])
    collar(poleDiameter+looseFit, 6, 5, screwBore);
    translate([150,15,0])
    collar(poleDiameter+looseFit, 6, 5, screwBore);
    translate([170,0,0])
    washer(poleDiameter+looseFit,3,standardWasherDepth);
    translate([170,10,0])
    washer(poleDiameter+looseFit,3,standardWasherDepth);
    translate([170,20,0])
    washer(poleDiameter+looseFit,3,standardWasherDepth);
    translate([170,30,0])
    washer(poleDiameter+looseFit,3,standardWasherDepth);
    translate([170,40,0])
    washer(poleDiameter+looseFit,3,standardWasherDepth);
    translate([170,50,0])
    washer(poleDiameter+looseFit,3,standardWasherDepth);
    translate([170,60,0])
    washer(poleDiameter+looseFit,3,standardWasherDepth);
    translate([170,70,0])
    washer(poleDiameter+looseFit,3,standardWasherDepth);
}


module motorHoles(){
    // screw holes
    outerHeight = 40.6;
    outerWidth = 25.5;
    holeBlockDiameter = 7.4;
    deltaX = outerWidth - holeBlockDiameter;
    deltaY = outerHeight - holeBlockDiameter;

    motorShaftDeltaY = 30.56 - motorShaftDiameter/2 - holeBlockDiameter/2;
    
    rotate([0,0,180]) translate([-deltaX/2,-motorShaftDeltaY,0]){
        // screw holes
        for(x=[0, deltaX], y=[0, deltaY]) translate([x,y,0]) {
            cylinder(d=m3Hole,h=6);
        }

        // motor shaft hole
        translate([deltaX/2,motorShaftDeltaY,0]) {
            cylinder(d=motorShaftDiameter+3*looseFit,h=6);
        }
    }
}


// chainGear(motorShaftDiameter, motorKeyDiameter, tightFit);
// chainGear_v2();
// motorHoles();
// fullAssembly();
printReady();
// motorHousing();
// chainGuide();


